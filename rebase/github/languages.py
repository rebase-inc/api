from base64 import b64decode
from collections import defaultdict, Counter
from datetime import datetime
from logging import getLogger
from os.path import splitext, join, isdir
from shutil import rmtree
from time import sleep

from github import GithubException

from rebase.github.api import RebaseGithub, RebaseGithubException
from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from rebase.common.debug import pdebug
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


logger = getLogger(__name__)
github_logger = getLogger('github')
# set the level to 'DEBUG' to open the firehose of data from PyGithub
github_logger.setLevel('INFO')


EXTENSION_TO_LANGUAGES = defaultdict(list)
for language, extension_list in _language_list.items():
    for extension in extension_list:
        EXTENSION_TO_LANGUAGES[extension].append(language)


CLONED_REPOS_ROOT_DIR = '/repos'


class UnsupportedContentEncoding(Exception):

    message_format = 'Unsupported Github content encoding "{}" for "{}"'.format

    def __init__(url, encoding):
        self.message = UnsupportedContentEncoding.message_format(encoding, url)


def decode(content_file):
    if not content_file.content:
        logger.warning('Empty content at URL: %s', content_file.url)
        return ''
    if content_file.encoding == 'base64':
        return b64decode(content_file.content).decode()
    else:
        raise UnsupportedContentEncoding(content_file.encoding, content_file.url)


def scan_one_commit_with_github(api, repo, commit):
    # remember, we MUST pop this 'context' when we are done with this session
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
                filename = file.filename
                if file_status == 'modified' and file.patch:
                    if filename not in all_files_before_commit:
                        pdebug(all_files_before_commit, 'all files before commit')
                        e = Exception()
                        setattr(e, 'message', '{} not found in previous files'.format(filename))
                        raise e
                    technologies.add(scan_tech_in_patch(
                        filename,
                        decode(repo.get_file_contents(filename, commit.sha)),
                        decode(repo.get_git_blob(all_files_before_commit[filename])),
                        file.patch,
                        commit.commit.author.date
                    ))
                elif file.status == 'added':
                    technologies.add(scan_tech_in_contents(
                        filename,
                        decode(repo.get_file_contents(filename, commit.sha)),
                        commit.commit.author.date
                    ))
                else:
                    pdebug(file, 'No patch here')
                    # TODO handle 'removed' and other status
            except SyntaxError as e:
                logger.warning('Syntax error: %s', e)
            except GithubException as e:
                logger.warning('GithubException Status: %d, Data: %s', e.status, e.data)
                raise e
            except RebaseGithubException as rebase_exception:
                logger.warning(rebase_exception)
                raise rebase_exception
    return commit_count_by_language, unknown_extension_counter, technologies


def scan_commits_with_github(api, owned_repos, login):
    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()
    technologies = TechProfile()
    for repo in owned_repos:
        logger.debug('processing repo %s', repo)
        try:
            for commit in repo.get_commits(author=login):
                _commit_count_by_language, _unknown_extensions, _technologies = scan_one_commit_with_github(api, repo, commit)
                #pdebug(_technologies, '_technologies')
                commit_count_by_language.update(_commit_count_by_language)
                unknown_extension_counter.update(_unknown_extensions)
                technologies.add(_technologies)
        except GithubException as e:
            logger.debug('Caught Github Exception. Status: %d Data: %s', e.status, e.data)
            logger.debug('Skipping repo: %s', repo.name)
            break
    return commit_count_by_language, unknown_extension_counter, technologies


def scan_one_commit_on_disk(local_repo, commit):
    technologies = TechProfile()
    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()
    local_commit = local_repo.commit(commit.sha)
    pdebug(local_commit, 'local_commit')
    if local_commit.parents:
        if len(local_commit.parents) > 1:
            # merge commit, ignore it
            return commit_count_by_language, unknown_extension_counter, technologies
        else:
            for diff in local_commit.parents[0].diff(local_commit, create_patch=True):
                if diff.deleted_file or diff.renamed:
                    continue
                _, extension = splitext(diff.b_path if diff.new_file else diff.a_path)
                languages = EXTENSION_TO_LANGUAGES[extension.lower()]
                commit_count_by_language.update(languages)
                if not languages:
                    unknown_extension_counter.update([extension.lower()])
                # TODO write a scanner for each language
                if 'Python' in languages:
                    try:
                        if diff.new_file:
                            technologies.add(scan_tech_in_contents(
                                diff.b_path,
                                local_commit.tree[diff.b_path].data_stream.read().decode(),
                                local_commit.authored_datetime
                            ))
                        else:
                            technologies.add(scan_tech_in_patch(
                                diff.b_path,
                                local_commit.tree[diff.b_path].data_stream.read().decode(),
                                local_commit.parents[0].tree[diff.a_path].data_stream.read().decode(),
                                diff.diff.decode('UTF-8'),
                                local_commit.authored_datetime
                            ))
                    except SyntaxError as e:
                        logger.warning('Syntax error: %s', e)
                    except GithubException as e:
                        logger.warning('GithubException Status: %d, Data: %s', e.status, e.data)
                        raise e
                    except RebaseGithubException as rebase_exception:
                        logger.warning(rebase_exception)
                        raise rebase_exception
    else:
        logger.info('This commit has no parent: %s', local_commit.summary)
        for blob in local_commit.tree.traverse(lambda i,d: i.type=='blob'):
            _, extension = splitext(blob.name)
            languages = EXTENSION_TO_LANGUAGES[extension.lower()]
            commit_count_by_language.update(languages)
            if not languages:
                unknown_extension_counter.update([extension.lower()])
            # TODO write a scanner for each language
            if 'Python' in languages:
                try:
                    technologies.add(scan_tech_in_contents(
                        blob.name,
                        blob.data_stream.read().decode(),
                        local_commit.authored_datetime
                    ))
                except SyntaxError as e:
                    logger.warning('Syntax error: %s', e)
                except GithubException as e:
                    logger.warning('GithubException Status: %d, Data: %s', e.status, e.data)
                    raise e
                except RebaseGithubException as rebase_exception:
                    logger.warning(rebase_exception)
                    raise rebase_exception

    return commit_count_by_language, unknown_extension_counter, technologies


def scan_commits_on_disk(api, token, owned_repos, login):
    from git import Repo
    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()
    technologies = TechProfile()
    new_url_prefix = 'https://'+token+'@github.com'
    assert isdir(CLONED_REPOS_ROOT_DIR)
    for repo in owned_repos:
        logger.debug('processing repo %s', repo)
        repo_url = repo.clone_url
        oauth_url = repo_url.replace('https://github.com', new_url_prefix, 1)
        logger.debug('oauth_url: %s', oauth_url)
        local_repo_dir = join(CLONED_REPOS_ROOT_DIR, repo.name)
        if isdir(local_repo_dir):
            rmtree(local_repo_dir)
        local_repo = Repo.clone_from(oauth_url, local_repo_dir)
        try:
            for commit in repo.get_commits(author=login):
                _commit_count_by_language, _unknown_extensions, _technologies = scan_one_commit_on_disk(local_repo, commit)
                #pdebug(_technologies, '_technologies')
                commit_count_by_language.update(_commit_count_by_language)
                unknown_extension_counter.update(_unknown_extensions)
                technologies.add(_technologies)
        except GithubException as e:
            logger.debug('Caught Github Exception. Status: %d Data: %s', e.status, e.data)
            logger.debug('Skipping repo: %s', repo.name)
            break
        rmtree(local_repo_dir)
    return commit_count_by_language, unknown_extension_counter, technologies


def detect_languages(account_id):
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)
    author = github_session.account.github_user.login
    api = RebaseGithub(github_session.account.access_token)
    owned_repos = api.get_user().get_repos()

    (
        commit_count_by_language,
        unknown_extension_counter,
        technologies
    ) = scan_commits_on_disk(
        api,
        github_session.account.access_token,
        owned_repos,
        author
    )

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


