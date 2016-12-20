from collections import defaultdict, Counter
from logging import getLogger
from os.path import splitext, join, isdir
from pickle import dumps
from shutil import rmtree

from git import Repo
from git.exc import GitCommandError
from github import GithubException
from rq import Queue

from ..common.aws import s3_delete_folder, exists, s3, s3_wait_till_exists, S3Value
from ..common.debug import pdebug
from ..common import config
from ..common.stopwatch import InfoElapsedTime
from ..datetime import time_to_epoch
from ..skills.python import Python
from ..skills.aws_keys import (
    level_key,
    profile_key,
    public_profile_key,
    old_profile_key,
    old_public_profile_key,
)
from ..skills.java import Java
from ..skills.javascript import Javascript
from ..skills.metrics import measure
from ..skills.jvm_parser import JVMParser
from ..skills.tech_profile import TechProfile

from .api import RebaseGithub, RebaseGithubException
from .notifications import notifications_for


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
    'JavaScript': ('.js', '.jsx', '.es6'),
    'Clojure':  ('.clj',),
    'Swift':    ('.swift',),
    'Lua':      ('.lua',),
    'Scala':    ('.scala', '.sc'),
    'Go':       ('.go',),
}


logger = getLogger(__name__)


EXTENSION_TO_LANGUAGES = defaultdict(list)
for language, extension_list in _language_list.items():
    for extension in extension_list:
        EXTENSION_TO_LANGUAGES[extension].append(language)


# /repos is a tmpfs mounted drive
# meant for the 99% of repos less than 3GB that should fit in RAM.
# Anything bigger must use BIG_CLONED_REPOS_ROOT_DIR
CLONED_REPOS_ROOT_DIR = '/repos'


# this is where repos that can't fit in /repos go
BIG_CLONED_REPOS_ROOT_DIR = '/big_repos'


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
        assert isdir(BIG_CLONED_REPOS_ROOT_DIR)
        self.scanners = {

            'Python':       Python(),
            'JavaScript':   Javascript(),
            'Java':         Java(),

            #'C':        JVMParser('c'),
            #'C++':      JVMParser('cpp'),
            #'Clojure':  JVMParser('clojure'),
            #'Scala':    JVMParser('scala'),
            #'Go':       JVMParser('golang'),
            #'Lua':      JVMParser('lua'),
            #'Swift':    JVMParser('swift'),
        }
        self.supported_languages = set(self.scanners.keys())
        self.local_repo_dir = None

    def find_scanners(self, languages):
        for language in languages:
            if language in self.scanners:
                yield self.scanners[language]
            else:
                continue

    def close(self):
        for scanner in self.scanners.values():
            scanner.close()

    def scan_one_commit_on_disk(self, repo_name, commit):
        technologies = TechProfile()
        commit_count_by_language = Counter()
        unknown_extension_counter = Counter()
        local_commit = self.local_repo.commit(commit.sha)
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
                                technologies.merge(
                                    scanner.scan_contents(
                                        diff.b_path,
                                        local_commit.tree[diff.b_path].data_stream.read(),
                                        time_to_epoch(local_commit.authored_datetime),
                                        local_commit
                                    )
                                )
                            else:
                                technologies.merge(
                                    scanner.scan_diff(
                                        diff.b_path,
                                        local_commit.tree[diff.b_path].data_stream.read(),
                                        local_commit,
                                        local_commit.parents[0].tree[diff.a_path].data_stream.read(),
                                        local_commit.parents[0],
                                        time_to_epoch(local_commit.authored_datetime),
                                    )
                                )
                        except SyntaxError as e:
                            logger.exception('Syntax error while processing commit "%s"', local_commit.binsha)
                        except GithubException as e:
                            logger.exception('GithubException while processing commit "%s"', local_commit.binsha)
                        except RebaseGithubException as rebase_exception:
                            logger.exception()
                            raise rebase_exception
                        except Exception as last_chance:
                            logger.exception('in rebase.github.account_scanner.AccountScanner.scan_one_commit_on_disk: Uncaught exception')
        else:
            logger.info('This commit has no parent: %s', local_commit.summary)
            for blob in local_commit.tree.traverse(lambda i,d: i.type=='blob'):
                languages = count_languages(commit_count_by_language, unknown_extension_counter, blob.name)
                for scanner in self.find_scanners(languages):
                    try:
                        technologies.merge(scanner.scan_contents(
                            blob.name,
                            blob.data_stream.read(),
                            time_to_epoch(local_commit.authored_datetime),
                            local_commit
                        ))
                    except SyntaxError as e:
                        logger.warning('Syntax error: %s', e)
                    except GithubException as e:
                        logger.warning('GithubException Status: %d, Data: %s', e.status, e.data)
                        raise e
                    except RebaseGithubException as rebase_exception:
                        logger.warning(rebase_exception)
                        raise rebase_exception
                    except Exception as last_chance:
                        logger.exception('in rebase.github.account_scanner.AccountScanner.scan_one_commit_on_disk: Uncaught exception')

        return commit_count_by_language, unknown_extension_counter, technologies

    def clone_from(self, repo, oauth_url):
        if isdir(self.local_repo_dir):
            rmtree(self.local_repo_dir)
        logger.debug('Repo "{}" is cloning into {}'.format(repo.name, self.local_repo_dir))
        self.local_repo = Repo.clone_from(oauth_url, self.local_repo_dir)

    def clone(self, repo, oauth_url):
        '''

            Clone either in tmpfs ('/repos') or on container host drive ('/big_repos')

        '''
        # repo.size appears to be in KB
        clone_in_RAM = config.REPOS_VOLUME_SIZE_IN_MB > config.CLONE_SIZE_SAFETY_FACTOR * (repo.size/1024)
        if clone_in_RAM:
            self.local_repo_dir = join(CLONED_REPOS_ROOT_DIR, repo.name)
            logger.debug('Clone in RAM')
        else:
            self.local_repo_dir = join(BIG_CLONED_REPOS_ROOT_DIR, repo.name)
            logger.debug('Clone on disk')
        try:
            self.clone_from(repo, oauth_url)
        except GitCommandError:
            if clone_in_RAM:
                # try on disk
                self.local_repo_dir = join(BIG_CLONED_REPOS_ROOT_DIR, repo.name)
                logger.debug('Re-try cloning on disk')
                self.clone_from(repo, oauth_url)
        #logger.debug('SIZE: Github Repo Size: %d KB', repo.size)
        #from subprocess import check_output
        #out = check_output(('du', '-k', '-s', self.local_repo_dir))
        #logger.debug('SIZE: Local repo size: %d KB', int(out.decode().split('\t')[0]))

    def clone_if_not_cloned_already(self, repo):
        if self.cloned:
            logger.debug('Repo "{}" is already cloned'.format(repo.name))
            return
        repo_url = repo.clone_url
        oauth_url = repo_url.replace('https://github.com', self.new_url_prefix, 1)
        self.clone(repo, oauth_url)
        self.cloned = True

    def process_repo(self, repo, login, commit_count_by_language, unknown_extension_counter, technologies):
        logger.info('processing repo: "%s"', repo.name)
        self.cloned = False
        kwargs = { 'author': login } if login else {}
        try:
            for commit in repo.get_commits(**kwargs):
                # we only clone if there is at least one commit.
                self.clone_if_not_cloned_already(repo)
                _commit_count_by_language, _unknown_extensions, _technologies = self.scan_one_commit_on_disk(repo.name, commit)
                #pdebug(_technologies, '_technologies')
                commit_count_by_language.update(_commit_count_by_language)
                unknown_extension_counter.update(_unknown_extensions)
                technologies.merge(_technologies)
        except GithubException as e:
            logger.exception('Caught Github Exception while processing repo "%s"', repo.name)
        except Exception as last_chance:
            logger.exception('In rebase.github.account_scanner.AccountScanner.process_repo: Uncaught exception')
        # keep algo O(1) in space
        if self.local_repo_dir and isdir(self.local_repo_dir):
            rmtree(self.local_repo_dir)

    def scan_all_repos(
        self,
        notify_to_be_scanned_repos,
        notify_scanning,
        notify_scanned_repos,
        expire_notifications_keys,
        login=None,
    ):
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

        # we use an 'args' array so we don't have to manipulate GithubObject.NotSet ...
        args = [login] if login else []
        scanned_user = self.api.get_user(*args)
        logger.info('Scanning all repos for user: %s', scanned_user.login)
        logger.debug('oauth_scopes: %s', self.api.oauth_scopes)
        repos_to_be_scanned = []
        for repo in scanned_user.get_repos():
            try:
                repo_name = repo.name
            except GithubException as e:
                logger.exception('Could not fetch repo name')
                continue
            if config.ONLY_SCAN_THIS_REPO and (repo_name != config.ONLY_SCAN_THIS_REPO):
                logger.debug('Skipping repo %s, we only look at repo %s', repo.name, config.ONLY_SCAN_THIS_REPO)
                continue
            try:
                repo_languages = set(repo.get_languages().keys())
            except GithubException as e:
                logger.exception('Could not get languages for repo %s', repo_name)
                repo_languages = self.supported_languages
            except Exception as last_chance:
                logger.exception('Catch all exception while doing repo.get_languages')
                repo_languages = self.supported_languages
            finally:
                if bool(self.supported_languages & repo_languages):
                    self.cloned = False
                    repos_to_be_scanned.append(repo)
                else:
                    logger.debug('We do not support any of these languages: %s', repo_languages)

        notify_to_be_scanned_repos(repo.name for repo in repos_to_be_scanned)
        for repo in repos_to_be_scanned:
            notify_scanning(repo.name)
            self.process_repo(
                repo,
                scanned_user.login,
                commit_count_by_language,
                unknown_extension_counter,
                technologies
            )
            notify_scanned_repos(repo.name)
        notify_scanning(None)
        expire_notifications_keys()

        return commit_count_by_language, unknown_extension_counter, technologies


def save(data, user, private_scanning):
    '''

        Returns a tuple ('new_data', 'old_data')
        where 'new_data' is a S3Value object pointing at the new profile
        and 'old_data' is a S3Value object pointing at the old profile.
        The value of 'old_data' is potentially None if this is the first time a user is being scan for the given mode (public or private)

        We need to use S3Value objects because the 'old/new_data' is shared
        between independent services and therefore we must resolve the 'eventual consistency' of S3 data.

    '''
    if private_scanning:
        key = profile_key(user)
        old_data_key = old_profile_key(user)
    else:
        key = public_profile_key(user)
        old_data_key = old_public_profile_key(user)
    # save the previous data, so we later retrieve it and remove it from the rankings
    old_s3_value = None
    if exists(key):
        old_s3_object = s3.Object(config.S3_BUCKET, old_data_key)
        old_s3_object.copy_from(CopySource={
            'Bucket': config.S3_BUCKET,
            'Key': key
        })
    s3_object = s3.Object(config.S3_BUCKET, key)
    s3_object.put(Body=dumps(data))
    return key


def scan_one_user(token, token_user, user_login=None, contractor_id=None):
    user_data = dict()
    private_scanning = (user_login == None)
    scanned_user = user_login if user_login else token_user
    start_msg = 'processing Github user: ' + scanned_user
    try:
        scanner = AccountScanner(token, token_user)
        with InfoElapsedTime(start=start_msg, stop=start_msg+' took %f seconds'):
            # this is bound to be very confusing:
            # when scanning, user_login should be None for the Autenticated User
            # so private scanning: token_user (guy logged in), user_login= None
            # public scanning token_user=CRAWLER_USERNAME, user_login=<any user login>
            commit_count_by_language, unknown_extension_counter, technologies = scanner.scan_all_repos(
                *notifications_for(contractor_id),
                login=user_login,
            )
        scanner.close()
        user_data['commit_count_by_language'] = commit_count_by_language
        user_data['technologies'] = technologies
        user_data['unknown_extension_counter'] = unknown_extension_counter
        user_data['metrics'] = measure(technologies)
        user_data['rankings'] = dict()
        Queue(name='population').enqueue_call(
            'rebase.skills.population.update_rankings',
            args=(
                scanned_user,
                *save(user_data, scanned_user, private_scanning)
            ),
            kwargs={
                'contractor_id': contractor_id,
                'private': private_scanning
            },
            timeout=3600
        )
        return user_data
    except TimeoutError as timeout_error:
        logger.ERROR('scan_one_user(%s, %s) %s', token_user, user_login, str(timeout_error))
        return None


def delete_population():
    s3_delete_folder(config.S3_BUCKET, level_key(''))


def delete_user_profiles():
    s3_delete_folder(config.S3_BUCKET, 'user-profiles')


