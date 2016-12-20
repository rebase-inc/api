import os
from github import Github

CLONE_RAM_DIR = '/repos'
CLONE_FS_DIR = '/big_repos'

class GithubCommitCrawler(object):
    def __init__(self, access_token, notify_callback):
        self.github = Github(login_or_token = access_token)
        self.notify = notify_callback 
        self._in_memory_clone_limit = 1024 * os.environ['REPOS_VOLUME_SIZE_IN_MB'] / os.environ['CLONE_SIZE_SAFETY_FACTOR']

        commit_count_by_language = Counter()
        unknown_extension_counter = Counter()
        technologies = TechProfile()

    def crawl_all_repos(self)
        user = self.github.get_user()
        repos_to_crawl = []
        for repo in user.get_repos():
            try:
                languages = set(repo.get_languages().keys())
                if bool(self.supported_languages & languages):
                    repos_to_crawl.append(repo)
                else:
                    LOGGER.debug('Skipping repository "{}" because we have no support for any of these languages: {}'.format(repo, languages))
            except GithubException as e:
                LOGGER.exception('Unknown exception for user "{}" and repository "{}": {}'.format(user, repo, e))
        #self.notify('TO_BE_SCANNED', repos_to_scan)
        for repo in repos_to_scan:
            self.crawl_repo(repo)

    def crawl_repo(self, repo):
        all_commits = repo.get_commits({ author: self.user.login })
        if not len(all_commits):
            LOGGER.debug('Skipping {} repo (no commits found for user {})'.format(repo.name, self.user.login))
        else:
            cloned_repo = self.clone(repo, oauth_url)
            for commit in repo.get_commits({ author: self.user.login }):
                data = self.analyze_commit(cloned_repo.commit(commit.sha))

    def analyze_commit(self, commit):
        if len(commit.parents) == 0:
            return self.analyze_initial_commit(commit)
        elif len(commit.parents) == 1:
            return self.analyze_regular_commit(commit)
        else:
            return self.analyze_merge_commit(commit)

    def analyze_merge_commit(self, commit):
        return

    def analyze_initial_commit(self, commit):
        for blob in commit.tree.traverse(predicate = lambda item, depth: item.type == 'blob'):
            LOGGER.debug('We are reading some data from an initial commit: {}...'.format(blob.data_stream.read().decode()[:10]))

    def analyze_regular_commit(self, commit):
        for diff in commit.parents[0].diff(commit, create_path = True):
            if diff.deleted_file or diff.renamed:
                continue
            elif diff.new_file:  
                LOGGER.debug('We are reading some data for a new file: {}...'.format(commit.tree[diff.b_path].data_stream.read().decode()[:10]))
            else:
                LOGGER.debug('We are reading some data for a diff: {}... {}...'.format(
                    local_commit.tree[diff.b_path].data_stream.read().decode()[:10],
                    local_commit.parents[0].tree[diff.a_path].data_stream.read().decode()[:10],
                    )
    
    def clone(self, repo, oauth_url):
        clone_base_dir = CLONE_RAM_DIR if repo.size <= self._in_memory_clone_limit else CLONE_FS_DIR
        repo_path = os.path.join(clone_base_dir, repo.name)
        try: 
            git.Repo.clone_from(oauth_url, repo_path)
        except GitCommandError as e:
            if clone_base_dir == CLONE_RAM_DIR:
                LOGGER.exception('Failed to clone {} repository into memory ({}), trying to clone to disk...'.format(repo.name, e)) 
                repo_path = os.path.join(CLONE_FS_DIR, repo.name)
                git.Repo.clone_from(oauth_url, repo_path)
            else:
                raise e
        return repo_path


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
