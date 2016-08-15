from contextlib import contextmanager
from logging import getLogger
from os import makedirs
from os.path import isdir, join
from pickle import dump

from rebase.common.stopwatch import InfoElapsedTime
from rebase.github.languages import GithubAccountScanner


logger = getLogger(__name__)


DATA_ROOT = '/crawler'


def scan_user(user_login, token, batch_id=None):
    logger.debug('scan_user: [%s, %s, %s]', user_login, token, batch_id)
    user_data = dict()
    start_msg = 'processing Github user: '+user_login
    try:
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


