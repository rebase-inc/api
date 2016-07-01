from ast import parse, walk, Import, ImportFrom
from base64 import b64decode
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from logging import getLogger
from os.path import dirname, split

from rebase.common.debug import pdebug
from rebase.skills.tech_profile import TechProfile


logger = getLogger()


LANGUAGE_PREFIX = 'Python.'


_syntax_error_fields = ['filename', 'lineno', 'offset', 'text']


def safe_parse(code, filename):
    try:
        return parse(code, filename)
    except SyntaxError as syntax_error:
        logger.debug('======== Syntax Error ========')
        for f in _syntax_error_fields:
            logger.debug('{}: %s'.format(f), getattr(syntax_error, f))
        pdebug(code, 'Code')
        raise syntax_error


def split_dir(dir):
    '''
    Return an iterator over the elements of directory 'dir'.
    '''
    elements = []
    _dir = dir
    while True:
        _dir, leaf = split(_dir)
        elements.append(leaf)
        if not _dir:
            break
    return tuple(reversed(elements))


class InvalidImportFromLevel(Exception):
    def __init__(self, filename):
        self.message = 'Invalid ast.ImportFrom node level'


def module(import_from_node, filename):
    '''
    Return the proper module path equivalent to the . or .., etc. syntax
    with ImportFrom, when used in the form:
    from .. import Foo as Bar
    '''
    if import_from_node.module:
        return import_from_node.module
    module_elements = split_dir(dirname(filename))
    level = import_from_node.level - 1
    if level > 0:
        module_elements = module_elements[:-level]
    elif level < 0:
        raise InvalidImportFromLevel(filename)
    return '.'.join(module_elements)

    
def extract_prefixes(code, filename):
    ''' return prefixes where prefixes is a dictionary where a key is a sub-component of a techs 
     (e.g. 'sqlalchemy.orm') and the value is a list of prefixes (['sa', 'sqlalchemy.orm'])
     prefixes is thus a collection of search keywords to be applied on the commit patches
    '''
    tree = safe_parse(code, filename)
    prefixes = defaultdict(list)
    for node in walk(tree):
        if isinstance(node, Import):
            for _alias in node.names:
                if _alias.asname:
                    prefixes[_alias.name].append(_alias.asname)
                prefixes[LANGUAGE_PREFIX+_alias.name].append(_alias.name)
        if isinstance(node, ImportFrom):
            for _alias in node.names:
                sub_component = module(node, filename)+'.'+_alias.name
                prefixes[LANGUAGE_PREFIX+sub_component].append(_alias.asname if _alias.asname else _alias.name)
    return prefixes


def language_use(code, filename, date):
    ''' returns a dict of language elements to dates counter
    '''
    tree = safe_parse(code, filename)
    exposure = TechProfile()
    for node in walk(tree):
        exposure[LANGUAGE_PREFIX+'__language__.'+node.__class__.__name__].update([date])
    return exposure


def language_exposure(new_code, old_code, filename, date):
    new_language_use = language_use(new_code, filename, date)
    old_language_use = language_use(old_code, filename, date)
    abs_diff = TechProfile()
    all_keys = set(new_language_use) | set(old_language_use)
    for k in all_keys:
        # not the best option, but until we can diff 2 abstract syntax trees,
        # we can only look at the aggregate change
        use_count = abs(new_language_use[k][date] - old_language_use[k][date])
        if use_count > 0:
            abs_diff[k][date] = use_count
    return abs_diff


def tech_exposure(code, prefixes, date):
    ''' Return a dictionary in which each key is a tech item
    and each value is a list of date, one for each time the user
    has introduced the key in the code
    '''
    exposure = TechProfile()
    for component, keywords in prefixes.items():
        for prefix in keywords:
            for line in code:
                if prefix in line:
                    exposure[component].update([date])
    #pdebug(exposure, 'Technology Exposure')
    return exposure


class UnsupportedContentEncoding(Exception):

    message_format = 'Unsupported Github content encoding "{}" for "{}"'.format

    def __init__(url, encoding):
        self.message = UnsupportedContentEncoding.message_format(encoding, url)


def decode(content_file):
    if not content_file.content:
        logger.debug('Empty content at URL: %s', content_file.url)
        return ''
    if content_file.encoding == 'base64':
        return b64decode(content_file.content).decode()
    else:
        raise UnsupportedContentEncoding(content_file.encoding, content_file.url)


def scan_tech_in_patch(api, repo, file, previous_version_sha, date):
    filename = file.filename
    python_code = decode(repo.get_contents(filename))
    previous_code = decode(repo.get_git_blob(previous_version_sha))
    prefixes = extract_prefixes(python_code, filename)
    # taken the original patch and remove:
    # - context lines
    # - deleted lines
    # - comments
    reduced_patch = []
    for line in file.patch.splitlines():
        if line.startswith('+'):
            line = line[1:].lstrip()
            if line:
                if line[0] == '#':
                    continue
                reduced_patch.append(line)
    total_exposure = TechProfile()
    # we can use 'update' here because keys for tech and language exposure don't overlap
    # otherwise, we would use 'add'
    total_exposure.update(tech_exposure(reduced_patch, prefixes, date))
    total_exposure.update(language_exposure(python_code, previous_code, filename, date))
    return total_exposure


def scan_tech_in_contents(api, repo, file, date):
    filename = file.filename
    python_code = decode(repo.get_contents(filename))
    prefixes = extract_prefixes(python_code, file.filename)
    return tech_exposure(python_code, prefixes, date)


