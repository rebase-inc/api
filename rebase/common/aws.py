from boto3 import resource
from botocore.exceptions import ClientError


from rebase.common.settings import config


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


s3_exists_waiter = s3.meta.client.get_waiter('object_exists')


def s3_wait_till_exists(bucket, key):
    s3_exists_waiter.wait(
        Bucket=bucket,
        Key=key
    )


