from bisect import bisect_left, insort_left
from functools import partial
from logging import getLogger
from pickle import loads, dumps

from botocore.exceptions import ClientError

from rebase.common.aws import exists as s3_exists, s3, s3_wait_till_exists
from rebase.common.database import DB
from rebase.common.settings import config
from rebase.models import Contractor
from rebase.skills.impact_client import ImpactClient

from .aws_keys import profile_key, old_profile_key, level_key


logger = getLogger(__name__)


bucket = config['S3_BUCKET']


population_cache = dict()

IMPACT_CLIENT = ImpactClient()


def unpickle_s3_object(key):
    try:
        return loads(s3.Object(bucket, key).get()['Body'].read())
    except ClientError as e:
        logger.debug('unpickle_s3_object(bucket={}, key={}) caught an exception: %o'.format(bucket, key), e.response['Error'])


def s3_get(key):
    is_population_key = key.startswith('population')
    if is_population_key:
        if key in population_cache:
            return population_cache[key]
        else:
            obj = unpickle_s3_object(key)
            population_cache[key] = obj
            return obj
    return unpickle_s3_object(key)


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
    contractor_id=None,
    get=s3_get,
    put=s3_put,
    exists=s3_exists,
    wait_till_exists=s3_wait_till_exists
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

    '''
    all_scores = dict()
    old_metrics_key = old_profile_key(user) 
    if exists(old_metrics_key):
        old_metrics = get(old_metrics_key)['metrics']
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
                    # rq_population. If rq_population crashes before it can update the scores,
                    # there will be an inconsistency.
                    # Clearly, rq_population should never crash & there should never be an inconsistency
                    # but since the goal here is to remove the key from scores anyways, that key not being
                    # here is not really a problem!
                    logger.exception('Cannot find old score for level {} in metrics'.format(level))
            else:
                scores = list()
            all_scores[level] = scores
    user_data_key = profile_key(user)
    if not exists(user_data_key):
        wait_till_exists(user_data_key)
    new_user_data = get(user_data_key) 
    new_metrics = new_user_data['metrics']
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
    update_user_rankings(user, contractor_id, get=get, exists=exists, put=put)


def get_rankings(user, get=s3_get, exists=s3_exists):
    rankings = dict()
    user_profile_key = profile_key(user)
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

def update_user_rankings(user, contractor_id=None, get=s3_get, exists=s3_exists, put=s3_put):
    user_data_key = profile_key(user)
    new_user_data = get(user_data_key) 
    profile_with_rankings = new_user_data
    rankings = get_rankings(user, get=get, exists=exists)
    profile_with_rankings['rankings'] = rankings
    put(user_data_key, profile_with_rankings)
    if contractor_id:
        from rebase.app import create
        app = create()
        with app.app_context():
            contractor = Contractor.query.get(contractor_id)
            if not contractor:
                logger.error('There is no Contractor with id[%d]', contractor_id)
            else:
                contractor.skill_set.skills = {}
                for package, rank in rankings.items():
                    impact = IMPACT_CLIENT.score(*package.split('.'))
                    contractor.skill_set.skills[package] = { 'impact': impact, 'rank': rank }
                DB.session.commit()


