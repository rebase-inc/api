from logging import DEBUG, basicConfig
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    basicConfig(**app.config['WEB_LOG_CONFIG'])
    handler = RotatingFileHandler(app.config['WEB_LOG_FILENAME'], maxBytes=10*(1024**2), backupCount=5)
    handler.setLevel(DEBUG)
    app.logger.addHandler(handler)


