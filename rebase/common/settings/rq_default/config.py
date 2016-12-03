from os import environ as env

from ..all_services import config as root_config


# treat the root config as immutable
config = dict(root_config)


config.update({
    'CLONE_SIZE_SAFETY_FACTOR':     int(env['CLONE_SIZE_SAFETY_FACTOR']),
    'CRAWLER_USERNAME':             env['CRAWLER_USERNAME'],
    'CRAWLER_PASSWORD':             env['CRAWLER_PASSWORD'],
    'GITHUB_APP_ID':                env['GITHUB_APP_ID'],
    'GITHUB_APP_SECRET':            env['GITHUB_APP_SECRET'],
    'GITHUB_CODE2RESUME_ID':        env['GITHUB_CODE2RESUME_ID'],
    'GITHUB_CODE2RESUME_SECRET':    env['GITHUB_CODE2RESUME_SECRET'],
    'ONLY_THIS_REPO':               env['ONLY_THIS_REPO'] if 'ONLY_THIS_REPO' in env else None,
    'REPOS_VOLUME_SIZE_IN_MB':      int(env['REPOS_VOLUME_SIZE_IN_MB']),
    'SERVICE_NAME':                 'rq_default',
    'QUEUES':                       ['default'],
})


