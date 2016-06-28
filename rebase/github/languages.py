from collections import defaultdict, Counter, namedtuple
from logging import getLogger
from os.path import splitext
from time import sleep

from rq.job import JobStatus

from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from rebase.common.debug import pdebug
from rebase.github import GithubApiFlaskOAuthlib, GithubException
from rebase.github.python import scan_tech_in_patch, scan_tech_in_contents
from rebase.github.session import create_admin_github_session
from rebase.models import (
    Contractor,
    SkillSet,
)
from rebase.skills.tech_profile import TechProfile


_language_list = {
    'Python':   ('.py',),
    'CSS':      ('.css',),
    'HTML':     ('.html',),
    'Bash':     ('.sh',),
    'Ruby':     ('.rb',),
    'Perl':     ('.pl',),
    'C':        ('.c', '.h'),
    'C++':      ('.cc', '.cxx', '.c++', '.cpp', '.hh', '.hxx', '.h++', '.hpp', '.h'),
    'Java':     ('.java',),
    'ObjectiveC': ('.m', '.mm', '.h'),
    'JavaScript': ('.js',),
    'Clojure':  ('.clj',)
}


logger = getLogger()


EXTENSION_TO_LANGUAGES = defaultdict(list)
for language, extension_list in _language_list.items():
    for extension in extension_list:
        EXTENSION_TO_LANGUAGES[extension].append(language)


def scan_one_commit(account_id, commit_url):
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)
    github_api = GithubApiFlaskOAuthlib(github_session.api)
    commit = github_api.get(commit_url)
    if commit['parents']:
        parent_commit = github_api.get(commit['parents'][0]['url'])
        parent_tree = github_api.get(parent_commit['commit']['tree']['url']+'?recursive=1')
        if parent_tree['truncated']:
            # TODO support recursive tree queries with truncated results
            logger.warning('Truncated tree for commit: %s', commit_url)
        all_files_before_commit = { component['path']: component['url'] for component in parent_tree['tree'] }
    else:
        logger.info('This commit has no parent: %s', commit)

    technologies = TechProfile()
    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()

    for file_obj in commit['files']:
        _, extension = splitext(file_obj['filename'])
        languages = EXTENSION_TO_LANGUAGES[extension.lower()]
        commit_count_by_language.update(languages)
        if not languages:
            unknown_extension_counter.update([extension.lower()])
        # TODO write a scanner for each language
        if 'Python' in languages:
            try:
                file_status = file_obj['status']
                if file_status == 'modified' and 'patch' in file_obj:
                    filename = file_obj['filename']
                    if filename not in all_files_before_commit:
                        pdebug(all_files_before_commit, 'all files before commit')
                        pdebug(commit, 'commit:')
                        e = Exception()
                        setattr(e, 'message', '{} not found in previous files'.format(filename))
                        raise e
                    technologies.add(scan_tech_in_patch(
                        github_api,
                        file_obj,
                        all_files_before_commit[filename],
                        commit['commit']['author']['date']
                    ))
                elif file_obj['status'] == 'added':
                    technologies.add(scan_tech_in_contents(github_api, file_obj, commit['commit']['author']['date']))
                else:
                    pdebug(file_obj, 'No patch here')
                    # TODO handle 'removed' and other status
            except Exception as e:
                if hasattr(e, 'message'):
                    logger.debug(e.message)
                logger.debug(e)
                raise e
    context.pop()
    return commit_count_by_language, unknown_extension_counter, technologies


class Queues(object):

    def __init__(self):
        self.high_queue = None
        self.default_queue = None
        self.low_queue = None


def scan_commits(account_id, github_api, owned_repos, login):
    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()

    technologies = TechProfile()

    scan_one_commit_jobs = set()
    from rebase.features.rq import setup_rq
    queues = Queues()
    setup_rq(queues)

    for repo in owned_repos:
        logger.debug('processing repo [{name}]'.format(**repo))
        try:
            commits = github_api.get('{url}/commits'.format(**repo), data={ 'author': login })
            repo_commits = {
                queues.default_queue.enqueue(
                    scan_one_commit,
                    args=(account_id, commit['url']),
                    meta={'url': commit['url']},
                    timeout=60
                ) for commit in commits
            }
            logger.info('Enqueued {} jobs for repo "{}"'.format(len(repo_commits), repo['name']))
            scan_one_commit_jobs.update(repo_commits)

        except GithubException as e:
            logger.debug('Caught Github Error Message: %s', e.message)
            logger.debug('Skipping repo: %s', repo['name'])
            break
    while scan_one_commit_jobs:
        logger.info('Sleeping 3 seconds')
        sleep(3)
        finished_jobs = filter(lambda job: job.get_status() in [JobStatus.FINISHED, JobStatus.FAILED], scan_one_commit_jobs)
        for finished_job in finished_jobs:
            if finished_job.get_status() == JobStatus.FINISHED:
                _commit_count_by_language, _unknown_extensions, _technologies = finished_job.result
                #logger.debug('Finished commit job for '+finished_job.meta['url'])
                pdebug(_technologies, '_technologies')
                commit_count_by_language.update(_commit_count_by_language)
                unknown_extension_counter.update(_unknown_extensions)
                technologies.add(_technologies)
            scan_one_commit_jobs.remove(finished_job)
    return commit_count_by_language, unknown_extension_counter, technologies


def detect_languages(account_id):
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)
    author = github_session.account.github_user.login
    owned_repos = github_session.api.get('/user/repos').data

    commit_count_by_language, unknown_extension_counter, technologies = scan_commits(account_id, GithubApiFlaskOAuthlib(github_session.api), owned_repos, author)

    pdebug(technologies, 'Tech Profile')
    pdebug(str(technologies), 'Tech Profile')
    scale_skill = lambda number: (1 - (1 / (0.01*number + 1 ) ) )
    contractor = next(filter(lambda r: r.type == 'contractor', github_session.account.user.roles), None) or Contractor(github_session.acccount.user)
    contractor.skill_set.skills = { language: scale_skill(commits) for language, commits in commit_count_by_language.items() }
    github_session.account.remote_work_history.analyzing = False
    DB.session.commit()
    invalidate([(SkillSet, (contractor.skill_set.id,))])

    pdebug(contractor.skill_set.skills, '{} Skills'.format(contractor))
    for extension, count in unknown_extension_counter.most_common():
        logger.warning('Unrecognized extension "{}" ({} occurrences)'.format(extension, count))
    # popping the context will close the current database connection.
    context.pop()

