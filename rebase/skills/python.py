from ast import parse, walk, Import, ImportFrom
from collections import defaultdict, Counter
from copy import copy
from datetime import datetime, timedelta
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


def tech_exposure(code, prefixes, date):
    ''' Return a dictionary in which each key is a tech item
    and each value is a list of date, one for each time the user
    has introduced the key in the code
    '''
    exposure = TechProfile()
    for component, keywords in iteritems(prefixes):
        for prefix in keywords:
            for line in code.splitlines():
                if prefix in line:
                    exposure[component].update([date])
    #pdebug(exposure, 'Technology Exposure')
    return exposure


class PythonScanner(TechnologyScanner):

    def safe_parse(self, code, filename):
        try:
            return parse(code, filename)
        except SyntaxError as syntax_error:
            logger.debug('======== Syntax Error:  ========')
            for f in _syntax_error_fields:
                logger.debug('{}: %s'.format(f), getattr(syntax_error, f))
            pdebug(code, 'Code')
            raise syntax_error

    def language_use(self, code, filename, date):
        ''' returns a dict of language elements to dates counter
        '''
        tree = self.safe_parse(code, filename)
        exposure = TechProfile()
        for node in walk(tree):
            exposure[LANGUAGE_PREFIX+'__language__.'+node.__class__.__name__].update([date])
        return exposure


    def language_exposure(self, new_code, old_code, filename, date):
        new_language_use = self.language_use(new_code, filename, date)
        old_language_use = self.language_use(old_code, filename, date)
        abs_diff = TechProfile()
        all_keys = set(new_language_use) | set(old_language_use)
        for k in all_keys:
            # not the best option, but until we can diff 2 abstract syntax trees,
            # we can only look at the aggregate change
            use_count = abs(new_language_use[k][date] - old_language_use[k][date])
            if use_count > 0:
                abs_diff[k][date] = use_count
        return abs_diff


    def extract_prefixes(self, code, filename):
        ''' return prefixes where prefixes is a dictionary where a key is a sub-component of a techs 
         (e.g. 'sqlalchemy.orm') and the value is a list of prefixes (['sa', 'sqlalchemy.orm'])
         prefixes is thus a collection of search keywords to be applied on the commit patches
        '''
        tree = self.safe_parse(code, filename)
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

    def scan_patch(self, filename, code, previous_code, patch, date):
        '''
            filename:  string identifying the 'code'
            code: string containing the code to be analyzed
            previous_code: string with the previous version of the code
            patch: string with the corresponding diff between code and previous_code
            date: string with ISO 8601 formatted date
        '''
        prefixes = self.extract_prefixes(code, filename)
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
        total_exposure = TechProfile()
        # we can use 'update' here because keys for tech and language exposure don't overlap
        # otherwise, we would use 'add'
        total_exposure.update(tech_exposure('\n'.join(reduced_patch), prefixes, date))
        total_exposure.update(self.language_exposure(code, previous_code, filename, date))
        return total_exposure

    def scan_contents(self, filename, code, date):
        prefixes = self.extract_prefixes(code, filename)
        return tech_exposure(code, prefixes, date)


