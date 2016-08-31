from ast import parse, walk, Import, ImportFrom
import ast
from collections import defaultdict
from inspect import getmro
from logging import getLogger
from os.path import dirname, split

from rebase.common.debug import pdebug
from rebase.skills.tech_profile import TechProfile
from rebase.skills.technology_scanner import TechnologyScanner


logger = getLogger(__name__)


LANGUAGE_PREFIX = 'Python.'


_syntax_error_fields = ('filename', 'lineno', 'offset', 'text')


def language():
    _language = set()
    super_nodes = set()
    prefix = 'Python.__language__.'
    for name, node in ast.__dict__.items():
        if isinstance(node, type) and issubclass(node, ast.AST):
            _language.add(prefix+name)
            mro = getmro(node)
            if len(mro) > 3:
                super_nodes.add(mro[1].__name__)
    for n in super_nodes:
        _language.remove(prefix+n)
    return _language


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


def safe_parse(code, filename):
    try:
        return parse(code, filename)
    except SyntaxError as syntax_error:
        logger.debug('======== Syntax Error:  ========')
        for f in _syntax_error_fields:
            logger.debug('{}: %s'.format(f), getattr(syntax_error, f))
        #pdebug(code, 'Code')
        raise syntax_error


class PythonScanner(TechnologyScanner):

    def extract_library_bindings(self, code, filename):
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
                        library_bindings[LANGUAGE_PREFIX+_alias.name].append(_alias.asname)
                    library_bindings[LANGUAGE_PREFIX+_alias.name].append(_alias.name)
            if isinstance(node, ImportFrom):
                for _alias in node.names:
                    sub_component = module(node, filename)+'.'+_alias.name
                    library_bindings[LANGUAGE_PREFIX+sub_component].append(_alias.asname if _alias.asname else _alias.name)
        return library_bindings

    def grammar_use(self, code, date):
        '''
            Returns a TechProfile of abstract grammar elements in 'code'
            by walking through the abstract syntax tree of the code.

            See https://docs.python.org/3.5/library/ast.html#abstract-grammar
            for details.

            Raises SyntaxError if parsing fails.
        '''
        tree = safe_parse(code, '')
        grammar_profile = TechProfile()
        for node in walk(tree):
            grammar_profile.add(LANGUAGE_PREFIX+'__language__.'+node.__class__.__name__, date, 1)
        return grammar_profile


