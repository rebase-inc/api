from collections import defaultdict, Counter
from logging import getLogger
from os.path import splitext
from pickle import load

from rebase.cache.rq_jobs import invalidate
from rebase.github.session import GithubSession, make_admin_github_session
from rebase.models import (
    Contractor,
    SkillSet,
)


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


def detect_languages(account_id):
    github_session = make_admin_github_session(account_id)

    author = github_session.account.login
    owned_repos = github_session.api.get('/user/repos').data

    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()

    for repo in owned_repos:
        logger.debug('processing repo [{name}]'.format(**repo))
        commits = github_session.api.get('{url}/commits'.format(**repo), data={ 'author': author }).data
        for commit in commits:
            commit = github_session.api.get(commit['url']).data
            for file_obj in commit['files']:
                _, extension = splitext(file_obj['filename'])
                languages = EXTENSION_TO_LANGUAGES[extension.lower()]
                commit_count_by_language.update(languages)
                if not languages:
                    unknown_extension_counter.update([extension.lower()])

    scale_skill = lambda number: (1 - (1 / (0.01*number + 1 ) ) )
    contractor = next(filter(lambda r: r.type == 'contractor', github_session.account.user.roles), None) or Contractor(github_session.acccount.user)
    contractor.skill_set.skills = { language: scale_skill(commits) for language, commits in commit_count_by_language.items() }
    github_session.account.remote_work_history.analyzing = False
    github_session.DB.session.commit()
    invalidate([(SkillSet, (contractor.skill_set.id,))])

    logger.debug('%s skills: %s', contractor, contractor.skill_set.skills)
    for extension, count in unknown_extension_counter.most_common():
        logger.warning('Unrecognized extension "{}" ({} occurrences)'.format(extension, count))
