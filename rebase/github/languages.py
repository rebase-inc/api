from collections import defaultdict, Counter
from os.path import splitext
from pickle import load
from pprint import pprint

from rebase.github.session import GithubSession, make_admin_github_session
from rebase.models import (
    Contractor,
    SkillSet,
)

languages = {
    'Python':   ('.py',),
    'Ruby':     ('.rb',),
    'Perl':     ('.pl',),
    'C':        ('.c', '.h'),
    'C++':      ('.cc', '.cxx', '.c++', '.cpp', '.hh', '.hxx', '.h++', '.hpp', '.h'),
    'Java':     ('.java',),
    'ObjectiveC': ('.m', '.mm', '.h'),
    'Javascript': ('.js',),
    'Clojure':  ('.clj',)
}

extension_to_languages = defaultdict(list)
for language, extensions in languages.items():
    for extension in extensions:
        extension_to_languages[extension].append(language)

all_extensions = []
for extensions in languages.values():
    for ext in extensions:
        all_extensions.append(ext)

def repo_commit_paths(session, repo):
    author = session.account.login
    author_filter = { 'author': author } if author else None
    commits = session.api.get(repo['url']+'/commits', data=author_filter).data
    for commit in commits:
        tree = session.api.get(commit['commit']['tree']['url']).data
        for path_obj in tree['tree']:
            yield path_obj['path']

def path_to_languages(commit_paths):
    all_languages = Counter()
    for path in commit_paths:
        _, extension = splitext(path)
        extension = extension.lower()
        if extension and extension in all_extensions:
            all_languages.update(set(extension_to_languages[extension]))
    return all_languages

def save_languages(user, languages, db):
    contractor_roles = tuple(filter(lambda role: role.type == 'contractor', user.roles))
    if not contractor_roles:
        contractor = Contractor(user)
        db.session.add(contractor)
    else:
        contractor = contractor_roles[0]
    total_commits = sum(languages.values())
    skill_set = contractor.skill_set
    skill_set.skills = { language: commits/total_commits for language, commits in languages.items() }
    db.session.add(skill_set)
    db.session.commit()
    return skill_set.skills

def detect_languages(account_id):
    ''' returns a list of all languages spoken by this user '''
    session = make_admin_github_session(account_id)
    owned_repos = session.api.get('/user/repos').data
    def all_commit_paths(repos):
        for repo in repos:
            print('processing repo [{}]'.format(repo['name']))
            for path in repo_commit_paths(session, repo):
                yield path

    found_languages = path_to_languages(all_commit_paths(owned_repos))
    skills = save_languages(session.account.user, found_languages, session.DB)
    pprint(found_languages)
    pprint(skills)
