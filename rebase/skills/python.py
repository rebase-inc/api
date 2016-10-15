from ast import parse, walk, Import, ImportFrom
import ast
from collections import defaultdict
from inspect import getmro
from logging import getLogger
from os.path import dirname, split

from stdlib_list import stdlib_list, long_versions

from rebase.common.debug import pdebug
from rebase.skills.tech_profile import TechProfile
from rebase.skills.technology_scanner import TechnologyScanner


logger = getLogger(__name__)


LANGUAGE_PREFIX = 'Python.'


_syntax_error_fields = ('filename', 'lineno', 'offset', 'text')

standard_library = set()
for version in long_versions:
    standard_library |= set(stdlib_list(version))


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
        Return a tuple (module_path, is_absolute),
        where module_path equivalent to the . or .., etc.
        Syntax with ImportFrom, when used in the form:
        from .. import Foo as Bar

        Examples:

        module(Import("pickle")) => ("pickle", true)
        module(ImportFrom("..foobar")) => ("rebase.foobar", false)


    '''
    if import_from_node.module:
        return import_from_node.module, True
    module_elements = split_dir(dirname(filename))
    level = import_from_node.level - 1
    if level > 0:
        module_elements = module_elements[:-level]
    elif level < 0:
        raise InvalidImportFromLevel(filename)
    return '.'.join(module_elements), False


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
        return LANGUAGE_PREFIX+'__standard_library__.'+module_name
    else:
        return LANGUAGE_PREFIX+'__third_party__.'+module_name


class PythonScanner(TechnologyScanner):

    def extract_library_bindings(self, code, filename):
        ''' 
            Return a dictionary for all libraries detected in 'code'
            with their local bindings in the 'code'.

            Note that it can also resolve relative imports, but since we cannot
            distinguish (right now) between third-party and private module, we ignore
            the relative imports because those we know are private.

            For instance:

            from sqlalchemy.orm import foo as bar
            import pickle

            would be listed as:
            {
                ...
                'Python.__third_party__.sqlalchemy.orm.foo': ['bar'],
                'Python.__standard_library__.pickle': ['pickle'],
                ...
            }

            See also 'rebase/tests/unit/skills_python.py'.

        '''
        tree = safe_parse(code, filename)
        library_bindings = defaultdict(list)
        for node in walk(tree):
            if isinstance(node, Import):
                # TODO: find a way to distinguish 3rd-party modules from private modules.
                for _alias in node.names:
                    if _alias.asname:
                        library_bindings[tech(_alias.name)].append(_alias.asname)
                    library_bindings[tech(_alias.name)].append(_alias.name)
            if isinstance(node, ImportFrom):
                module_name, is_absolute = module(node, filename)
                if is_absolute:
                    tech_prefix = tech(module_name)
                    for _alias in node.names:
                        tech_name = tech_prefix+'.'+_alias.name
                        library_bindings[tech_name].append(_alias.asname if _alias.asname else _alias.name)
                else:
                    logger.debug('Ignoring private module: '+module_name)
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
            grammar_profile.add(LANGUAGE_PREFIX+'__language__.'+node.__class__.__name__, date, 1)
        return grammar_profile


