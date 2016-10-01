from logging import getLogger
from pickle import loads

from rebase.common.aws import s3
from rebase.common.settings import config


logger = getLogger(__name__)


bucket = config['S3_BUCKET']


def update(user_data_key, user):
    logger.debug('population.update was called')
    logger.debug('user_data_key: %o', user_data_key)
    logger.debug('user: %o', user)

    pickled_user_data = s3.Object(bucket, user_data_key).get()['Body'].read()
    user_data = loads(pickled_user_data)
    logger.debug('user_data: %o', user_data)


