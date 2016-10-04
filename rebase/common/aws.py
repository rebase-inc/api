from boto3 import resource
from botocore.exceptions import ClientError


from rebase.common.settings import config


def exists(bucket, key):
    # why is this not provided by boto3?
    try:
        s3.Object(bucket, key).load()
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise e
    return True


s3 = resource(
    's3', 
    aws_access_key_id=config['BACKEND_AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=config['BACKEND_AWS_SECRET_ACCESS_KEY']
)


s3_exists_waiter = s3.meta.client.get_waiter('object_exists')


def s3_wait_till_exists(bucket, key):
    s3_exists_waiter.wait(
        Bucket=bucket,
        Key=key
    )


