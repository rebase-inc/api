from ast import parse, walk, Import, ImportFrom
import ast
from collections import defaultdict
from functools import partial
from inspect import getmro
from logging import getLogger
from os.path import dirname, split, splitext

from stdlib_list import stdlib_list, long_versions

from rebase.common.debug import pdebug
from .importable_modules import ImportableModules
from .tech_profile import TechProfile
from .technology_scanner import TechnologyScanner


logger = getLogger(__name__)


LANGUAGE_PREFIX = 'Python.'


_syntax_error_fields = ('filename', 'lineno', 'offset', 'text')


standard_library = set()
for version in long_versions:
    standard_library |= set(stdlib_list(version))


def language():
    _language = set()
    super_nodes = set()
    prefix = 'Python.__grammar__.'
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


def safe_parse(code, filename):
    try:
        return parse(code, filename)
    except SyntaxError as syntax_error:
        logger.debug('======== Syntax Error:  ========')
        for f in _syntax_error_fields:
            logger.debug('{}: %s'.format(f), getattr(syntax_error, f))
        #pdebug(code, 'Code')
        raise syntax_error


def tech(module_name):
    if module_name in standard_library:
        return LANGUAGE_PREFIX+'__std_library__.'+module_name
    else:
        return LANGUAGE_PREFIX+'__3rd_party__.'+module_name


class PythonScanner(TechnologyScanner):

    def extract_library_bindings(self, code, filename, context):
        ''' 
            Return a dictionary for all libraries detected in 'code'
            with their local bindings in the 'code'.

            Note that it can also resolve relative imports, but since we cannot
            distinguish (right now) between 3rd-party and private module, we ignore
            the relative imports because those we know are private.

            For instance:

            from sqlalchemy.orm import foo as bar
            import pickle

            would be listed as:
            {
                ...
                'Python.__3rd_party__.sqlalchemy.orm.foo': ['bar'],
                'Python.__std_library__.pickle': ['pickle'],
                ...
            }

            See also 'rebase/tests/unit/skills_python.py'.

        '''
        # TODO modify the Python scanner to take advantage of before and after modules from PythonContext
        importable_modules = frozenset(context[0])
        tree = safe_parse(code, filename)
        library_bindings = defaultdict(list)
        for node in walk(tree):
            if isinstance(node, Import):
                for _alias in node.names:
                    if _alias.name in importable_modules:
                        logger.debug('importing private module "{}"'.format(_alias.name))
                        continue
                    if _alias.asname:
                        library_bindings[tech(_alias.name)].append(_alias.asname)
                    library_bindings[tech(_alias.name)].append(_alias.name)
            if isinstance(node, ImportFrom):
                if node.level == 0:
                    if node.module in importable_modules:
                        # private module
                        continue
                    tech_prefix = tech(node.module)
                    for _alias in node.names:
                        tech_name = tech_prefix+'.'+_alias.name
                        library_bindings[tech_name].append(_alias.asname if _alias.asname else _alias.name)
        return library_bindings

    def grammar_use(self, code, date):
        '''
            Returns a TechProfile of abstract grammar elements in 'code'
            by walking through the abstract syntax tree of the code.

            See https://docs.python.org/3.5/library/ast.html#abstract-grammar
            for details.

            Raises SyntaxError if parsing fails.

            TODO: merge grammar_use and extract_library_bindings, 2 parsing passes is wasteful.
            We need to use the protocol described in remote_scanner_protocol.md which
            exposes a simple interface { scan_contents, scan_patch }.

        '''
        tree = safe_parse(code, '')
        grammar_profile = TechProfile()
        for node in walk(tree):
            grammar_profile.add(LANGUAGE_PREFIX+'__grammar__.'+node.__class__.__name__, date, 1)
        return grammar_profile

    def context(self, commit, parent_commit=None):
        return [
            tuple(ImportableModules(commit.tree)),
            tuple(ImportableModules(parent_commit.tree) if parent_commit else tuple())
        ]


