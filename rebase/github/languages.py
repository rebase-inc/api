from base64 import b64decode
from logging import getLogger
from os.path import join, isdir

from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from .account_scanner import scan_one_user
from rebase.github.session import create_admin_github_session
from rebase.models import (
    Contractor,
    SkillSet,
)


logger = getLogger(__name__)


def scan_public_and_private_repos(account_id):
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)
    account = github_session.account
    user_data = scan_one_user(account.access_token, account.github_user.login)
    logger.info(str(user_data['technologies']), 'Tech Profile')
    scale_skill = lambda number: (1 - (1 / (0.01*number + 1 ) ) )
    contractor = next(filter(lambda r: r.type == 'contractor', account.user.roles), None) or Contractor(github_session.acccount.user)
    contractor.skill_set.skills = { language: scale_skill(commits) for language, commits in user_data['commit_count_by_language'].items() }
    account.remote_work_history.analyzing = False
    DB.session.commit()
    invalidate([(SkillSet, (contractor.skill_set.id,))])
    logger.info(contractor.skill_set.skills, '{} Skills'.format(contractor))
    for extension, count in user_data['unknown_extension_counter'].most_common():
        logger.warning('Unrecognized extension "{}" ({} occurrences)'.format(extension, count))
    # popping the context will close the current database connection.
    context.pop()


