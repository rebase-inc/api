from contextlib import contextmanager
from logging import getLogger
from os import makedirs
from os.path import isdir, join
from pickle import dump

from redis import StrictRedis, TimeoutError

from rebase.common.stopwatch import InfoElapsedTime
from rebase.github.languages import GithubAccountScanner


logger = getLogger(__name__)


DATA_ROOT = '/crawler'


@contextmanager
def github_token(redis, token_list):
    logger.debug('waiting for token on '+token_list)
    try:
        token = redis.brpop(token_list, timeout=60)[1].decode()
    except TimeoutError as e:
        logger.warning(e)
        raise e
    logger.debug('got one token from '+token_list)
    yield token
    redis.lpushx(token_list, token)


def scan_user(user_login, token_list):
    user_data = dict()
    redis = StrictRedis(host='redis')
    start_msg = 'processing Github user: '+user_login
    try:
        with github_token(redis, token_list) as token:
            with InfoElapsedTime(start=start_msg, stop=start_msg+' took %f seconds'):
                commit_count_by_language, unknown_extension_counter, technologies = GithubAccountScanner(
                    token,
                    'rebase-dev'
                ).scan_all_repos(login=user_login)
            user_data['commit_count_by_language'] = commit_count_by_language
            user_data['technologies'] = technologies
            user_data['unknown_extension_counter'] = unknown_extension_counter
            user_data_dir = join(DATA_ROOT, user_login)
            user_data_path = join(user_data_dir, 'data')
            if not isdir(user_data_dir):
                makedirs(user_data_dir)
            with open(user_data_path, 'wb') as f:
                dump(user_data, f)
            return 'success'
    except TimeoutError as timeout_error:
        return str(timeout_error)

