from logging import getLogger


# with log level INFO or less, boto3 is spewing way too many messages
getLogger('boto3').setLevel('WARNING')
getLogger('botocore').setLevel('INFO')

from boto3 import resource
from botocore.exceptions import ClientError

from rebase.common import config


s3 = resource(
    's3',
    region_name='us-east-1',
    aws_access_key_id=config.BACKEND_AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.BACKEND_AWS_SECRET_ACCESS_KEY,
)


def exists(key, bucket = config.S3_BUCKET):
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


s3_exists_waiter = s3.meta.client.get_waiter('object_exists')


def s3_wait_till_exists(bucket, key):
    s3_exists_waiter.wait(Bucket = bucket, Key = key)


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


