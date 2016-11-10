from logging import INFO

# Settings that are common to all services

# This config will be loaded by each individual service setting and,
# if necessary, overwritten by them.

config = {
    'LOG_FORMAT': '%(levelname)s {%(processName)s[%(process)d]} %(message)s',
    'LOG_LEVEL': INFO,
    'RSYSLOG_CONFIG': {
        'address': ('rsyslog', 514),
    },
}
