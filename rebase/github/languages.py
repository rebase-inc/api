from collections import defaultdict, Counter
from os.path import splitext
from pickle import load

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

def repo_commit_paths(repo, author=None):
    author_filter = { 'author': author } if author else None
    commits = github.get(repo['url']+'/commits', data=author_filter).data
    for commit in commits:
        tree = github.get(commit['commit']['tree']['url']).data
        for path_obj in tree['tree']:
            yield path_obj['path']

def path_to_languages(commit_paths):
    all_languages = Counter()
    for paths in commit_paths:
        languages = []
        for path in paths:
            _, extension = splitext(path)
            extension = extension.lower()
            if extension and extension in all_extensions:
                languages.append(set(extension_to_languages[extension]))
        found_languages = Counter()
        ambiguous_languages = []
        for commit_languages in languages:
            if len(commit_languages) == 1:
                found_languages.update(commit_languages)
            else:
                ambiguous_languages.append(commit_languages)
        for ambi in ambiguous_languages:
            if ambi & found_languages:
                continue
            else:
                found_languages.update(ambi)
        all_languages.update(found_languages)
    return all_languages

def save_user_languages(user, languages, db):
    skill_set = SkillSet.query.join(Contractor).filter(Contractor.user == user).first()
    if not skill_set:
        raise RuntimeError('This contractor should have an associated SkillSet already')
    skill_set.skills = languages
    db.session.add(skill_set)
    db.session.commit()

def detect_user_languages(session):
    ''' returns a list of all languages spoken by this user '''
    owned_repos = session.api.get('/user/repos').data
    def all_commit_paths(repos):
        for repo in owned_repos:
            paths = repo_commit_paths(repo, author=session.login)
            yield next(paths)

    found_languages = path_to_languages(all_commit_paths)
    save_languages(session.user, found_languages, session.db)
    return found_languages


if __name__ == '__main__':
    with open('/tmp/paths.pickle', 'rb') as f:
        commit_paths = load(f)
    print(path_to_languages(commit_paths))
