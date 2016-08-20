from collections import defaultdict, Counter
from logging import getLogger
from os.path import splitext, join, isdir
from shutil import rmtree

from git import Repo
from github import GithubException, GithubObject

from rebase.common.debug import pdebug
from rebase.datetime import time_to_epoch
from rebase.github.api import RebaseGithub, RebaseGithubException
from rebase.github.py2_py3_scanner import Py2Py3Scanner
from rebase.skills.remote_scanner import Client
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
    'JavaScript': ('.js', '.jsx'),
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


def count_languages(commit_count_by_language, unknown_extension_counter, filepath):
    '''
    return a list of potential languages for the file at 'filepath'
    '''
    _, extension = splitext(filepath)
    languages = EXTENSION_TO_LANGUAGES[extension.lower()]
    commit_count_by_language.update(languages)
    if not languages:
        unknown_extension_counter.update([extension.lower()])
    return languages


class AccountScanner(object):

    def __init__(self, access_token, login):
        '''
            'login' is the Github login for which the 'access_token' was generated.
        '''
        self.api = RebaseGithub(access_token)
        # the authenticated user login:
        self.login = login
        self.new_url_prefix = 'https://'+access_token+'@github.com'
        assert isdir(CLONED_REPOS_ROOT_DIR)
        self.scanners = {
            'Python': Py2Py3Scanner(),
            'Javascript': Client('javascript')
        }

    def find_scanners(self, languages):
        for language in languages:
            if language in self.scanners:
                yield self.scanners[language]
            else:
                continue

    def close(self):
        for scanner in self.scanners:
            scanner.close()

    def scan_one_commit_on_disk(self, repo_name, local_repo, commit):
        technologies = TechProfile()
        commit_count_by_language = Counter()
        unknown_extension_counter = Counter()
        local_commit = local_repo.commit(commit.sha)
        pdebug(
            {
                'SHA1': local_commit.binsha,
                'Author': local_commit.author,
                'Message': local_commit.message
            },
            'Commit in repo: '+ repo_name
        )
        if local_commit.parents:
            if len(local_commit.parents) > 1:
                # merge commit, ignore it
                return commit_count_by_language, unknown_extension_counter, technologies
            else:
                for diff in local_commit.parents[0].diff(local_commit, create_patch=True):
                    if diff.deleted_file or diff.renamed:
                        continue
                    languages = count_languages(
                        commit_count_by_language,
                        unknown_extension_counter,
                        diff.b_path if diff.new_file else diff.a_path
                    )
                    for scanner in self.find_scanners(languages):
                        try:
                            if diff.new_file:
                                technologies.merge(scanner.scan_contents(
                                    diff.b_path,
                                    local_commit.tree[diff.b_path].data_stream.read().decode(),
                                    time_to_epoch(local_commit.authored_datetime)
                                ))
                            else:
                                technologies.merge(scanner.scan_patch(
                                    diff.b_path,
                                    local_commit.tree[diff.b_path].data_stream.read().decode(),
                                    local_commit.parents[0].tree[diff.a_path].data_stream.read().decode(),
                                    diff.diff.decode('UTF-8'),
                                    time_to_epoch(local_commit.authored_datetime)
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
                languages = count_languages(commit_count_by_language, unknown_extension_counter, blob.name)
                for scanner in self.find_scanners(languages):
                    try:
                        technologies.merge(scanner.scan_contents(
                            blob.name,
                            blob.data_stream.read().decode(),
                            time_to_epoch(local_commit.authored_datetime)
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

    
    def process_repo(self, repo, login, commit_count_by_language, unknown_extension_counter, technologies):
        logger.info('processing repo: "%s"', repo.name)
        repo_url = repo.clone_url
        oauth_url = repo_url.replace('https://github.com', self.new_url_prefix, 1)
        local_repo_dir = join(CLONED_REPOS_ROOT_DIR, repo.name)
        if isdir(local_repo_dir):
            rmtree(local_repo_dir)
        local_repo = Repo.clone_from(oauth_url, local_repo_dir)
        try:
            for commit in repo.get_commits(author=login if login != GithubObject.NotSet else self.login):
                _commit_count_by_language, _unknown_extensions, _technologies = self.scan_one_commit_on_disk(repo.name, local_repo, commit)
                #pdebug(_technologies, '_technologies')
                commit_count_by_language.update(_commit_count_by_language)
                unknown_extension_counter.update(_unknown_extensions)
                technologies.merge(_technologies)
        except GithubException as e:
            logger.warning('Caught Github Exception. Status: %d Data: %s', e.status, e.data)
            logger.warning('Skipping repo: %s', repo.name)
        # keep algo O(1) in space
        rmtree(local_repo_dir)

    def scan_all_repos(self, login=GithubObject.NotSet):
        '''
            'login' is the account that will be scanned.
            It may be a different login than the one provided with the access_token.
        '''
        commit_count_by_language = Counter()
        unknown_extension_counter = Counter()
        technologies = TechProfile()
        # Note: get_user returns 2 very differents objects depending on whether login is None or
        # not. If login is None, it returns an AuthenticatedUser, otherwise, a NamedUser.
        # get_repos() will then return all (public+private) repos for an AuthenticatedUser,
        # but only public repos for a NamedUser, EVEN IF NamedUser is the actual owner of the access token and scope has private repos!
        for repo in self.api.get_user(login).get_repos():
            self.process_repo(repo, login, commit_count_by_language, unknown_extension_counter, technologies)
        return commit_count_by_language, unknown_extension_counter, technologies


