from logging import INFO
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    handler = RotatingFileHandler(app.config['LOG_FILE'], maxBytes=10000000, backupCount=1)
    handler.setLevel(INFO)
    app.logger.addHandler(handler)

