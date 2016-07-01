from collections import defaultdict, Counter, namedtuple
from logging import getLogger
from os.path import splitext
from time import sleep

from github import Github, GithubException
from rq.job import JobStatus

from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from rebase.common.debug import pdebug
from rebase.features.rq import setup_rq
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


def scan_one_commit(token, repo_id, commit_sha):
    # remember, we MUST pop this 'context' when we are done with this session
    api = Github(token)
    repo = api.get_repo(repo_id)
    commit = repo.get_commit(commit_sha)
    technologies = TechProfile()
    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()
    if commit.parents:
        parent_commit = commit.parents[0].commit
        parent_tree = repo.get_git_tree(parent_commit.tree.sha, recursive=True)
        all_files_before_commit = { element.path: element.sha for element in parent_tree.tree }
    else:
        logger.info('This commit has no parent: %s', commit)

    for file in commit.files:
        _, extension = splitext(file.filename)
        languages = EXTENSION_TO_LANGUAGES[extension.lower()]
        commit_count_by_language.update(languages)
        if not languages:
            unknown_extension_counter.update([extension.lower()])
        # TODO write a scanner for each language
        if 'Python' in languages:
            try:
                file_status = file.status
                if file_status == 'modified' and file.patch:
                    filename = file.filename
                    if filename not in all_files_before_commit:
                        pdebug(all_files_before_commit, 'all files before commit')
                        e = Exception()
                        setattr(e, 'message', '{} not found in previous files'.format(filename))
                        raise e
                    technologies.add(scan_tech_in_patch(
                        api,
                        repo,
                        file,
                        all_files_before_commit[filename],
                        commit.commit.author.date
                    ))
                elif file.status == 'added':
                    technologies.add(scan_tech_in_contents(api, repo, file, commit.commit.author.date))
                else:
                    pdebug(file, 'No patch here')
                    # TODO handle 'removed' and other status
            except Exception as e:
                if hasattr(e, 'message'):
                    logger.debug(e.message)
                logger.debug(e)
                raise e
    return commit_count_by_language, unknown_extension_counter, technologies


class Queues(object):

    def __init__(self):
        self.high_queue = None
        self.default_queue = None
        self.low_queue = None


queues = Queues()


setup_rq(queues)


done_states = (JobStatus.FINISHED, JobStatus.FAILED)


def scan_commits(api, token, owned_repos, login):
    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()

    technologies = TechProfile()

    all_jobs = set()

    for repo in owned_repos:
        logger.debug('processing repo %s', repo)
        try:
            for commit in repo.get_commits(author=login):
                job = queues.default_queue.enqueue(
                    scan_one_commit,
                    args=(token, repo.id, commit.sha),
                    timeout=600
                )
                all_jobs.add(job)
        except GithubException as e:
            logger.debug('Caught Github Exception. Status: %d Data: %s', e.status, e.data)
            logger.debug('Skipping repo: %s', repo.name)
            break
    # now every 3 seconds, aggregate the commit_count, unknown extensions and technologies detected by finished jobs at that point
    while True:
        logger.info('Sleeping 3 seconds')
        sleep(3)
        finished_jobs = tuple(filter(lambda job: job.get_status() in done_states, all_jobs))
        for finished_job in finished_jobs:
            if finished_job.get_status() == JobStatus.FINISHED:
                _commit_count_by_language, _unknown_extensions, _technologies = finished_job.result
                pdebug(_technologies, '_technologies')
                commit_count_by_language.update(_commit_count_by_language)
                unknown_extension_counter.update(_unknown_extensions)
                technologies.add(_technologies)
            all_jobs.remove(finished_job)
        if not all_jobs:
            break
    return commit_count_by_language, unknown_extension_counter, technologies


def detect_languages(account_id):
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)
    author = github_session.account.github_user.login
    token = github_session.account.access_token
    api = Github(token)
    owned_repos = api.get_user().get_repos()

    (
        commit_count_by_language,
        unknown_extension_counter,
        technologies
    ) = scan_commits(
        api,
        token,
        owned_repos,
        author
    )

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

