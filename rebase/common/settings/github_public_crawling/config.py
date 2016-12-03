
from ..rq_default.config import config as base_config


config = dict(base_config)


config.update({
    'SERVICE_NAME': 'github_public_crawling',
    'QUEUES': ['github_public_crawling'],
})


