from os import environ


# Settings that are common to all derived settings,
# typically the dictionary declared in dev.py (for development) or pro.py (for production).

config = dict({
    'S3_BUCKET': environ['S3_BUCKET'],
    'LOG_FORMAT': '%(levelname)s {%(processName)s[%(process)d]} %(message)s',
    'RSYSLOG_CONFIG': {
        'address': ('rsyslog', 514),
    },

})
