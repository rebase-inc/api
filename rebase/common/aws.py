from boto3 import resource


from rebase.common.settings import config

s3 = resource(
    's3', 
    aws_access_key_id=config['BACKEND_AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=config['BACKEND_AWS_SECRET_ACCESS_KEY']
)


