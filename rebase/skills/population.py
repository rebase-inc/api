from bisect import bisect_left, insort_left
from functools import partial
from logging import getLogger
from pickle import loads, dumps

from botocore.exceptions import ClientError

from rebase.common.aws import exists, s3, s3_wait_till_exists
from rebase.common.settings import config
from .aws_keys import profile_key, old_profile_key, level_key


logger = getLogger(__name__)


bucket = config['S3_BUCKET']


population_cache = dict()



def unpickle_s3_object(key):
    try:
        return loads(s3.Object(bucket, key).get()['Body'].read())
    except ClientError as e:
        logger.debug('unpickle_s3_object(bucket={}, key={}) caught an exception: %o'.format(bucket, key), e.response['Error'])


def get(key):
    is_population_key = key.startswith('population')
    if is_population_key:
        if key in population_cache:
            return population_cache[key]
        else:
            obj = unpickle_s3_object(key)
            population_cache[key] = obj
            return obj
    return unpickle_s3_object(key)


def put(key, obj):
    if key.startswith('population'):
        population_cache[key] = obj
    s3_object = s3.Object(bucket, key)
    s3_object.put(Body=dumps(obj))


def update_rankings(
    user,
    get=get,
    put=put,
    exists=exists,
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
    user_data_key = profile_key(user)
    old_metrics_key = old_profile_key(user) 
    if exists(old_metrics_key):
        old_metrics = get(old_metrics_key)['metrics']
        for level, score in old_metrics.items():
            key = level_key(level)
            if exists(key):
                scores = get(key)
                i = bisect_left(scores, score)
                if not i:
                    raise ValueError('Cannot find old score for level {} in metrics'.format(level))
                del scores[i]
            else:
                scores = list()
            all_scores[level] = scores
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
        put('population/'+level, scores)
    update_user_rankings(user)


def get_rankings(user, get=get, exists=exists):
    rankings = dict()
    user_profile_key = profile_key(user)
    user_profile = get(user_profile_key) 
    metrics = user_profile['metrics']
    for level, score in metrics.items():
        key = level_key(level)
        if exists(key):
            scores = get(key)
        else:
            scores = list()
        index = bisect_left(scores, score)
        ranking = 100*(len(scores)-(index+1))/len(scores)
        rankings[level] = ranking
    return rankings


def update_user_rankings(user, get=get, exists=exists, put=put):
    user_data_key = profile_key(user)
    new_user_data = get(user_data_key) 
    profile_with_rankings = new_user_data
    profile_with_rankings['rankings'] = get_rankings(user)
    put(user_data_key, profile_with_rankings)

