from bisect import bisect_left, insort_left
from functools import partial
from logging import getLogger
from pickle import loads

from rebase.common.aws import exists as _exists, s3, s3_wait_till_exists
from rebase.common.settings import config


logger = getLogger(__name__)


bucket = config['S3_BUCKET']


population_cache = dict()


exists = partial(_exists, bucket=bucket)


def unpickle_s3_object(key):
    return loads(s3.Object(bucket, key).get()['Body'].read())


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
    user_data_key,
    user,
    get=get,
    put=put,
    exists=exists,
    wait_till_exists=s3_wait_till_exists
):
    '''

    Update the rankings now that 'user_data_key' has a new set of metrics
    1/ get the old metrics for this 'user'
    2/ load the relevant rankings (overall+languages)
    3/ remove from rankings the old metrics from 'user'
    4/ add the new metrics for 'user'
    5/ save the updated rankings

    Note:
    (get, put, exists, wait_till_exists) are abstracted out so we can test this function without S3.

    '''
    if exists('population/overall'):
        overall = get('population/overall')
    else:
        overall = list()
    languages = dict()
    old_metrics_key = user_data_key+'_old'
    if exists(old_metrics_key):
        old_metrics = get(old_metrics_key)['metrics']
        old_overall_score = old_metrics['overall']
        old_overall_score_index = bisect_left(overall, old_overall_score)
        if not i:
            raise ValueError('Cannot find old overall score in rankings')
        del overall[old_overall_score_index]
        for language, score in old_metrics['languages'].items():
            scores = get('population/languages/'+language)
            i = bisect_left(scores, score)
            if not i:
                raise ValueError('Cannot find old score for language {} in rankings'.format(language))
            del scores[i]
            languages[language] = scores
    if not exists(user_data_key):
        wait_till_exists(user_data_key)
    new_metrics = get(user_data_key)['metrics']
    insort_left(overall, new_metrics['overall'])
    for language, score in new_metrics['languages'].items():
        if language in languages:
            insort_left(languages[language], score)
        else:
            language_key = 'population/languages/'+language 
            if exists(language_key):
                scores = get(language_key)
            else:
                scores = list()
            insort_left(scores, score)
            languages[language] = scores
    for language, scores in languages.items():
        put('population/languages/'+language, scores)
    put('population/overall', overall)


def get_rankings(user):
    pass
