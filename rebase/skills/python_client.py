from ast import AST, parse, walk, Import, ImportFrom, Name
import ast
from collections import defaultdict, Counter
from functools import partial
from inspect import getmro
from logging import getLogger
from os.path import dirname, split, splitext

from six import iteritems
from stdlib_list import stdlib_list, long_versions

from rebase.common.debug import pdebug
from .importable_modules import ImportableModules
from .scanner_client import ScannerClient
from .technology_scanner import TechnologyScanner


logger = getLogger(__name__)


_syntax_error_fields = ('filename', 'lineno', 'offset', 'text')


standard_library = set()
for version in long_versions:
    standard_library |= set(stdlib_list(version))


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
        logger.exception('parse error with '+filename)
        raise syntax_error


def tech(module_name):
    if module_name in standard_library:
        return STD_LIB_PREFIX+module_name
    else:
        return THIRD_PARTY_LIB_PREFIX+module_name


class PythonClient(ScannerClient):

    def __init__(self):
        super(PythonClient, self).__init__()

    def languages(self):
        return 'Python',

    def grammar(self, language_index):
        _grammar = list()
        super_nodes = set()
        for name, node in ast.__dict__.items():
            if isinstance(node, type) and issubclass(node, AST):
                _grammar.append(name)
                mro = getmro(node)
                if len(mro) > 3:
                    super_nodes.add(mro[1].__name__)
        for n in super_nodes:
            _grammar.remove(n)
        return _grammar

    def scan_contents(self, language_index, filename, code, context):
        '''
            Return a dictionary of technologies to use count for 'code'
        '''
        tree = safe_parse(code, filename)
        importable_modules = frozenset(context)
        library_bindings = dict()
        profile = Counter()
        for node in walk(tree):
            profile.update(('0.'+node.__class__.__name__,))
            if isinstance(node, Import):
                for _alias in node.names:
                    module_name = _alias.name
                    if module_name in importable_modules:
                        #logger.debug('importing private module "{}"'.format(module_name))
                        continue
                    if module_name in standard_library:
                        update = partial(profile.update, ('1.'+module_name,))
                    else:
                        update = partial(profile.update, ('2.'+module_name,))
                    if _alias.asname:
                        library_bindings[_alias.asname] = update
                    else:
                        library_bindings[_alias.name] = update
                    update()
            if isinstance(node, ImportFrom):
                if node.level == 0:
                    if node.module in importable_modules:
                        #logger.debug('importing private module "{}"'.format(node.module))
                        continue
                    tech_prefix = node.module
                    if tech_prefix in standard_library:
                        tech_prefix = '1.'+tech_prefix
                    else:
                        tech_prefix = '2.'+tech_prefix
                    for _alias in node.names:
                        tech_name = tech_prefix+'.'+_alias.name
                        update = partial(profile.update, (tech_name,))
                        update()
                        if _alias.asname:
                            library_bindings[_alias.asname] = update
                        else:
                            library_bindings[_alias.name] = update
            if isinstance(node, Name):
                if node.id in library_bindings:
                    library_bindings[node.id]()

        return profile


