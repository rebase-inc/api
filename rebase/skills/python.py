from ast import parse, walk, Import, ImportFrom
from collections import defaultdict
from logging import getLogger
from os.path import dirname, split

from six import iteritems

from rebase.common.debug import pdebug
from rebase.skills.tech_profile import TechProfile
from rebase.skills.technology_scanner import TechnologyScanner


logger = getLogger(__name__)


LANGUAGE_PREFIX = 'Python.'


_syntax_error_fields = ('filename', 'lineno', 'offset', 'text')


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


def libraries_profile(code, library_bindings, date):
    '''
        Return a TechProfile object for libraries from 'code'.
    '''
    profile = TechProfile()
    for module, bindings in iteritems(library_bindings):
        for binding in bindings:
            for line in code.splitlines():
                if binding in line:
                    profile.add(module, date, 1)
    #pdebug(profile, 'Libraries profile')
    return profile


def safe_parse(code, filename):
    try:
        return parse(code, filename)
    except SyntaxError as syntax_error:
        logger.debug('======== Syntax Error:  ========')
        for f in _syntax_error_fields:
            logger.debug('{}: %s'.format(f), getattr(syntax_error, f))
        #pdebug(code, 'Code')
        raise syntax_error


def grammar_use(code, filename, date):
    '''
        Returns a TechProfile of abstract grammar elements in 'code'
        by walking through the abstract syntax tree of the code.

        See https://docs.python.org/3.5/library/ast.html#abstract-grammar
        for details.

        Raises SyntaxError if parsing fails.
    '''
    tree = safe_parse(code, filename)
    grammar_profile = TechProfile()
    for node in walk(tree):
        grammar_profile.add(LANGUAGE_PREFIX+'__language__.'+node.__class__.__name__, date, 1)
    return grammar_profile


def language_profile(new_code, old_code, filename, date):
    new_grammar_use = grammar_use(new_code, filename, date)
    if not old_code:
        return new_grammar_use
    old_grammar_use = grammar_use(old_code, filename, date)
    abs_diff = TechProfile()
    all_keys = set(new_grammar_use) | set(old_grammar_use)
    for technology in all_keys:
        # not the best option, but until we can diff 2 abstract syntax trees,
        # we can only look at the aggregate change
        use_count = abs(new_grammar_use[technology].total_reps - old_grammar_use[technology].total_reps)
        if use_count > 0:
            abs_diff.add(technology, date, use_count)
    return abs_diff


def extract_library_bindings(code, filename):
    ''' 
        Return a dictionary for all libraries detected in 'code'
        with their local bindings in the 'code'.
        Note that it can also resolve relative imports.

        For instance:

        'from sqlalchemy.orm import foo as bar'
        would be listed as:
        {
            ...
            'Python.sqlalchemy.orm.foo': ['bar'],
            ...
        }
    '''
    tree = safe_parse(code, filename)
    library_bindings = defaultdict(list)
    for node in walk(tree):
        if isinstance(node, Import):
            for _alias in node.names:
                if _alias.asname:
                    library_bindings[_alias.name].append(_alias.asname)
                library_bindings[LANGUAGE_PREFIX+_alias.name].append(_alias.name)
        if isinstance(node, ImportFrom):
            for _alias in node.names:
                sub_component = module(node, filename)+'.'+_alias.name
                library_bindings[LANGUAGE_PREFIX+sub_component].append(_alias.asname if _alias.asname else _alias.name)
    return library_bindings


class PythonScanner(TechnologyScanner):

    def scan_patch(self, filename, code, previous_code, patch, date):
        library_bindings = extract_library_bindings(code, filename)
        # taken the original patch and remove:
        # - context lines
        # - deleted lines
        # - comments
        reduced_patch = []
        for line in patch.splitlines():
            if line.startswith('+'):
                line = line[1:].lstrip()
                if line:
                    if line[0] == '#':
                        continue
                    reduced_patch.append(line)
        complete_profile = libraries_profile('\n'.join(reduced_patch), library_bindings, date)
        complete_profile.merge(language_profile(code, previous_code, filename, date))
        return complete_profile

    def scan_contents(self, filename, code, date):
        library_bindings = extract_library_bindings(code, filename)
        complete_profile = libraries_profile(code, library_bindings, date)
        complete_profile.merge(language_profile(code, '', filename, date))
        return complete_profile


