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

print(extension_to_languages)

all_extensions = []
for extensions in languages.values():
    for ext in extensions:
        all_extensions.append(ext)

print(all_extensions)

def path_to_languages(commit_paths):
    all_languages = set()
    for paths in commit_paths:
        languages = []
        for path in paths:
            _, extension = splitext(path)
            extension = extension.lower()
            if extension and extension in all_extensions:
                languages.append(set(extension_to_languages[extension]))
        print(languages)
        found_languages = set()
        ambiguous_languages = []
        for commit_languages in languages:
            if len(commit_languages) == 1:
                found_languages |= commit_languages
            else:
                ambiguous_languages.append(commit_languages)
                for languages in ambiguous_languages:
                    if languages & found_languages:
                        continue
                    else:
                        found_languages |= languages
        all_languages |= found_languages
    return all_languages

if __name__ == '__main__':
    with open('/tmp/paths.pickle', 'rb') as f:
        commit_paths = load(f)
    print(path_to_languages(commit_paths))
