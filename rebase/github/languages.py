from collections import defaultdict, Counter, namedtuple
from logging import getLogger
from os.path import splitext

from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from rebase.common.debug import pdebug
from rebase.github.session import create_admin_github_session
from rebase.models import (
    Contractor,
    SkillSet,
)
from rebase.github.python import scan_tech_in_commit


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
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)

    author = github_session.account.login
    owned_repos = github_session.api.get('/user/repos').data

    commit_count_by_language = Counter()
    unknown_extension_counter = Counter()

    technologies = TechProfile()

    commit_count = 0
    for repo in owned_repos:
        logger.debug('processing repo [{name}]'.format(**repo))
        if commit_count > 10:
            break
        commits = github_session.api.get('{url}/commits'.format(**repo), data={ 'author': author }).data
        for commit in commits:
            commit = github_session.api.get(commit['url']).data
            commit_count += 1
            if commit_count > 10:
                break

            for file_obj in commit['files']:
                _, extension = splitext(file_obj['filename'])
                languages = EXTENSION_TO_LANGUAGES[extension.lower()]
                commit_count_by_language.update(languages)
                if not languages:
                    unknown_extension_counter.update([extension.lower()])
                # TODO write a scanner for each language
                if 'Python' in languages:
                    if 'patch' in file_obj:
                        technologies.add(scan_tech_in_commit(github_session.api, file_obj, commit['commit']['author']['date']))
                    else:
                        pdebug(file_obj, 'No patch here')
                        # TODO handle 'added' & 'removed' status

    pdebug(technologies, 'Tech Profile')
    pdebug(str(technologies), 'Tech Profile')
    scale_skill = lambda number: (1 - (1 / (0.01*number + 1 ) ) )
    contractor = next(filter(lambda r: r.type == 'contractor', github_session.account.user.roles), None) or Contractor(github_session.acccount.user)
    contractor.skill_set.skills = { language: scale_skill(commits) for language, commits in commit_count_by_language.items() }
    contractor.skill_set.technologies = technologies
    github_session.account.remote_work_history.analyzing = False
    DB.session.commit()
    invalidate([(SkillSet, (contractor.skill_set.id,))])

    pdebug(contractor.skill_set.skills, '{} Skills'.format(contractor))
    for extension, count in unknown_extension_counter.most_common():
        logger.warning('Unrecognized extension "{}" ({} occurrences)'.format(extension, count))
    # popping the context will close the current database connection.
    context.pop()

