from bisect import insort_left
from logging import getLogger
from pickle import loads, dumps

from botocore.exceptions import ClientError
from rq import Queue

from ..common.aws import (
    exists as s3_exists,
    s3,
    s3_consistent_get,
    s3_wait_till_exists,
    unpickle_s3_object,
    S3Value,
)
from ..common.settings import config

from .aws_keys import (
    level_key,
    profile_key,
    public_profile_key,
    old_profile_key,
    old_public_profile_key,
)


logger = getLogger(__name__)


bucket = config['S3_BUCKET']


population_cache = dict()


def s3_get(key):
    is_population_key = key.startswith('population')
    if is_population_key:
        if key in population_cache:
            return population_cache[key]
        else:
            obj = unpickle_s3_object(bucket, key)
            population_cache[key] = obj
            return obj
    return unpickle_s3_object(bucket, key)


def s3_put(key, obj):
    serialized_obj = dumps(obj)
    if key.startswith('population'):
        # this way we are sure the data returned by 'get' is consistent
        # whether it comes from the in-memory cache or S3
        population_cache[key] = loads(serialized_obj) 
    s3_object = s3.Object(bucket, key)
    s3_object.put(Body=serialized_obj)


def update_rankings(
    user,
    new_user_profile,
    old_user_profile=None,
    contractor_id=None,
    private=True,
    consistent_get=s3_consistent_get,
    get=s3_get,
    put=s3_put,
    exists=s3_exists,
    wait_till_exists=s3_wait_till_exists,
    write_to_db=True
):
    '''

    Update the rankings now that 'user_data_key' has a new set of metrics
    1/ get the old metrics for this 'user'
    2/ load the relevant rankings 
    3/ remove from rankings the old metrics from 'user'
    4/ add the new metrics for 'user'
    5/ save the updated rankings

    Note:
    (get, put, exists, wait_till_exists) are abstracted out so we can test this function without S3.
    
    'private' is True by default and means we read the private profile of 'user'

    '''
    all_scores = dict()
    if old_user_profile:
        old_metrics = consistent_get(old_user_profile)['metrics']
        for level, score in old_metrics.items():
            key = level_key(level)
            if exists(key):
                scores = get(key)
                logger.debug('scores: %s', scores)
                logger.debug('score: %s', score)
                try:
                    i = scores.index(score)
                    del scores[i]
                except ValueError as e:
                    # it is an inconsistency, but it's a recoverable one.
                    # Here's an example where it can occur
                    # (found during development of rq_population, while it can temporarily be buggy.)
                    # old_metrics are saved by rq_default service, but scores are updated
                    # by rq_population. If rq_population crashes before it can update the scores,
                    # there will be an inconsistency.
                    # Clearly, rq_population should never crash & there should never be an inconsistency
                    # but since the goal here is to remove the key from scores anyways, that key not being
                    # here is not really a problem!
                    logger.exception('Cannot find old score for level {} in metrics'.format(level))
            else:
                scores = list()
            all_scores[level] = scores
    new_metrics = consistent_get(new_user_profile)['metrics']
    for level, score in new_metrics.items():
        if level in all_scores:
            scores = all_scores[level]
        else:
            key = level_key(level)
            if exists(key):
                scores = get(key)
            else:
                scores = list()
        insort_left(scores, score)
        all_scores[level] = scores
    for level, scores in all_scores.items():
        put(level_key(level), scores)
    if write_to_db:
        Queue().enqueue_call(
            'rebase.db_jobs.contractor.update_user_rankings',
            args=(user,),
            kwargs={
                'private':          private,
                'contractor_id':    contractor_id,
                'get':              get,
                'exists':           exists, 
                'put':              put,
            }
        )


def get_rankings(
    user,
    private,
    get=s3_get,
    exists=s3_exists,
    wait_till_exists=s3_wait_till_exists,
):
    rankings = dict()
    user_profile_key = profile_key(user) if private else public_profile_key(user)
    if not exists(user_profile_key):
        wait_till_exists(bucket, user_profile_key)
    user_profile = get(user_profile_key) 
    metrics = user_profile['metrics']
    for level, score in metrics.items():
        key = level_key(level)
        if exists(key):
            scores = get(key)
            try:
                index = scores.index(score)
            except ValueError as e:
                raise ValueError(
                    "Could not find score {} for user {} in population {}".format(
                        score,
                        user,
                        key
                    )
                )
            rankings[level] = (len(scores)-(index+1))/len(scores)
        else:
            rankings[level] = 0.0
    return rankings


def read(github_user, private=True, get=s3_get, exists=s3_exists):
    '''

        Returns a dictionary with the following keys: ['unknown_extension_counter', 'technologies', 'commit_count_by_language'].
        'github_user' is the Github login.
        If 'private' is True, loads the profile from a private scan, assuming it exists.

    '''
    user_data_key = profile_key(github_user) if private else public_profile_key(github_user)
    new_user_data = get(user_data_key) 
    return new_user_data


