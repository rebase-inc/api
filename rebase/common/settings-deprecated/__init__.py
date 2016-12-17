config = 
    'URL_PREFIX':                       environ['API_URL_PREFIX'],
    'REDIS_HOST':                       environ['REDIS_HOST'],
    'RSYSLOG_HOST':                     environ['RSYSLOG_HOST'],
    'RSYSLOG_PORT':                     environ['RSYSLOG_PORT'],
    'BACKEND_AWS_ACCESS_KEY_ID':        environ['BACKEND_AWS_ACCESS_KEY_ID'],
    'BACKEND_AWS_SECRET_ACCESS_KEY':    environ['BACKEND_AWS_SECRET_ACCESS_KEY'],
    'S3_BUCKET':                        environ['S3_BUCKET'],
    'GITHUB_APP_CLIENT_ID':             environ['GITHUB_APP_CLIENT_ID'],
    'GITHUB_APP_CLIENT_SECRET':         environ['GITHUB_APP_CLIENT_SECRET'],
    'SQLALCHEMY_DATABASE_URI':          '{driver}://{username}:@{host}/{url}'.format(
                                            driver = 'postgres',
                                            username = 'postgres',
                                            host = environ['DATABASE_HOST'],
                                            url = 'postgres' 
                                        ),
    'COOKIE_SECURE_HTTPPONLY':          { 'secure': True, 'httponly': False },
    'LOG_FORMAT':                       '%(levelname)s {%(processName)s[%(process)d]} %(message).900s',
    'LOG_LEVEL':                        INFO,
    'SQLALCHEMY_POOL_SIZE':             1,
    'SQLALCHEMY_MAX_OVERFLOW':          1,
    'SQLALCHEMY_TRACK_MODIFICATIONS':   False,
    
    
    ############# WHAT ARE THESE FOR? #################
    'DEBUG':                            False, 
    'TESTING':                          False,
    'CSRF_ENABLED':                     True,
    'MAX_CONTENT_LENGTH':               1024 * 1024,
}
