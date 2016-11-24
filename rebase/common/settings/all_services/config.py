from logging import INFO

# Settings that are common to all services

# This config will be loaded by each individual service setting and,
# if necessary, overwritten by them.

# Note regarding LOG_FORMAT
# Message format is truncating to 900 bytes to fit under RFC-3164 4.1 syslog Message Parts which limits messages to 1024 bytes.
# rsyslog has a higher limit, but we still run into 
# "OSError: [Errno 90] Message too large" exceptions when boto3 calls logger.info on all the data sent to S3.

# 900 characters allows for 124 characters for the stuff before %(message)

config = {
    'LOG_FORMAT': '%(levelname)s {%(processName)s[%(process)d]} %(message).900s',
    'LOG_LEVEL': INFO,
    'RSYSLOG_CONFIG': {
        'address': ('rsyslog', 514),
    },
}
