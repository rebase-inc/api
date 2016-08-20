from base64 import b64decode
from pickle import dump
from logging import getLogger
from os import makedirs
from os.path import join, isdir

from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from rebase.github.session import create_admin_github_session
from rebase.models import (
    Contractor,
    SkillSet,
)


logger = getLogger(__name__)


def detect_languages(account_id):
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)
    account = github_session.account
    scanner = GithubAccountScanner(account.access_token, account.github_user.login)
    commit_count_by_language, unknown_extension_counter, technologies = scanner.scan_all_repos()
    logger.debug('detect_languages, oauth_scopes: %s', scanner.api.oauth_scopes)
    user_data_dir = '/crawler/{}'.format(account.github_user.login)
    if not isdir(user_data_dir):
        makedirs(user_data_dir)
    with open(join(user_data_dir, 'private'), 'wb') as f:
        dump(technologies, f)
    logger.info(str(technologies), 'Tech Profile')
    scale_skill = lambda number: (1 - (1 / (0.01*number + 1 ) ) )
    contractor = next(filter(lambda r: r.type == 'contractor', github_session.account.user.roles), None) or Contractor(github_session.acccount.user)
    contractor.skill_set.skills = { language: scale_skill(commits) for language, commits in commit_count_by_language.items() }
    github_session.account.remote_work_history.analyzing = False
    DB.session.commit()
    invalidate([(SkillSet, (contractor.skill_set.id,))])
    logger.info(contractor.skill_set.skills, '{} Skills'.format(contractor))
    for extension, count in unknown_extension_counter.most_common():
        logger.warning('Unrecognized extension "{}" ({} occurrences)'.format(extension, count))
    # popping the context will close the current database connection.
    context.pop()


