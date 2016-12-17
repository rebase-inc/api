from logging import INFO

# Settings that are common to all services

# Note regarding LOG_FORMAT
# Message format is truncating to 900 bytes to fit under RFC-3164 4.1 syslog Message Parts which limits messages to 1024 bytes.
# rsyslog has a higher limit, but we still run into 
# "OSError: [Errno 90] Message too large" exceptions when boto3 calls logger.info on all the data sent to S3.

# 900 characters allows for 124 characters for the stuff before %(message)

config = {
    'LOG_FORMAT': '%(levelname)s {%(processName)s[%(process)d]} %(message).900s',
    'LOG_LEVEL': INFO,
    'RSYSLOG_HOST': environ['RSYSLOG_HOST'],
    'RSYSLOG_PORT': environ['RSYSLOG_PORT'],
    'BACKEND_AWS_ACCESS_KEY_ID': environ['BACKEND_AWS_ACCESS_KEY_ID'],
    'BACKEND_AWS_SECRET_ACCESS_KEY': environ['BACKEND_AWS_SECRET_ACCESS_KEY'],
    'LOG_LEVEL': DEBUG,
    'S3_BUCKET': environ['S3_BUCKET'],
}
