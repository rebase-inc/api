from collections import namedtuple
from logging import getLogger
from pickle import loads

# with log level INFO or less, boto3 is spewing way too many messages
getLogger('boto3').setLevel('WARNING')
getLogger('botocore').setLevel('INFO')
from boto3 import resource
from botocore.exceptions import ClientError

from rebase.common.settings import config


logger = getLogger(__name__)


s3 = resource(
    's3', 
    region_name='us-east-1',
    aws_access_key_id=config['BACKEND_AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=config['BACKEND_AWS_SECRET_ACCESS_KEY']
)


bucket = config['S3_BUCKET']


def exists(key, bucket=bucket):
    # why is this not provided by boto3?
    try:
        s3.Object(bucket, key).load()
    except ClientError as e:
        code = e.response['Error']['Code']
        if  code == '404' or code == '403':
            # fucking hell: 403 Forbidden is reported for a fully permitted resource that doesn't exists...
            return False
        else:
            raise e
    return True


def unpickle_s3_object(bucket, key):
    try:
        return loads(s3.Object(bucket, key).get()['Body'].read())
    except ClientError as e:
        logger.debug('unpickle_s3_object(bucket={}, key={}) caught an exception: %o'.format(bucket, key), e.response['Error'])


s3_exists_waiter = s3.meta.client.get_waiter('object_exists')


def s3_wait_till_exists(bucket, key, etag=None):
    kwargs = {
        'Bucket':   bucket,
        'Key':      key,
    }
    if etag:
        kwargs['IfMatch'] = etag
    logger.debug('s3_wait_till_exists kwargs: %s', kwargs)
    s3_exists_waiter.wait(**kwargs)


# S3Value represents the value of a key with a certain hash
# It allows synchronisation of processes around future values
# that are not yet available for reading.
# See: https://en.wikipedia.org/wiki/Eventual_consistency
S3Value = namedtuple('S3Value', ('bucket', 'key', 'etag'))


def s3_consistent_get(value):
    assert isinstance(value, S3Value)
    s3_wait_till_exists(
        value.bucket,
        value.key,
        etag=value.etag
    )
    return unpickle_s3_object(value.bucket, value.key)


def s3_delete_folder(bucket, folder):
    args = {
        'Bucket': bucket,
        'Prefix': folder,
    }
    continuationToken = ''
    while True:
        if continuationToken:
            args['ContinuationToken'] = continuationToken
        response = s3.meta.client.list_objects_v2(**args)
        objects = response['Contents']
        s3.meta.client.delete_objects(
            Bucket=bucket,
            Delete={
                'Quiet': True,
                'Objects': [ { 'Key': obj['Key'] } for obj in objects ]
            }
        )
        if 'NextContinuationToken' in response:
            continuationToken = response['NextContinuationToken']
        else:
            break


