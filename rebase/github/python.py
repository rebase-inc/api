from ast import parse, walk, Import, ImportFrom
from base64 import b64decode
from collections import defaultdict
from datetime import datetime, timedelta

from rebase.common.debug import pdebug


LANGUAGE_PREFIX = 'Python.'
    

def extract_prefixes(code):
    tree = parse(code, 'string')
    # prefixes is a dictionary where a key is a sub-component of a techs 
    # (e.g. 'sqlalchemy.orm') and the value is a list of prefixes (['sa', 'sqlalchemy.orm'])
    # prefixes is thus a collection of search keywords to be applied on the commit patches
    prefixes = defaultdict(list)
    for node in walk(tree):
        if isinstance(node, Import):
            for _alias in node.names:
                if _alias.asname:
                    prefixes[_alias.name].append(_alias.asname)
                prefixes[LANGUAGE_PREFIX+_alias.name].append(_alias.name)
        if isinstance(node, ImportFrom):
            for _alias in node.names:
                sub_component = node.module+'.'+_alias.name
                prefixes[LANGUAGE_PREFIX+sub_component].append(_alias.asname if _alias.asname else _alias.name)
    return prefixes


def extract_technology_exposure(code, prefixes, date):
    ''' Return a dictionary in which each key is a tech item
    and each value is a list of date, one for each time the user
    has introduced the key in the code
    '''
    exposure = defaultdict(list)
    for component, keywords in prefixes.items():
        for prefix in keywords:
            for line in code:
                if prefix in line:
                    exposure[component].append(date)
    #pdebug(exposure, 'Technology Exposure')
    return exposure


def scan_tech_in_patch(api, file_obj, date):
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    LANGUAGE_PREFIX = 'Python.'
    python_code = b64decode(api.get(file_obj['contents_url']).data['content'])
    prefixes = extract_prefixes(python_code)
    #pdebug(prefixes, 'Prefixes')
    # taken the original patch and remove:
    # - context lines
    # - deleted lines
    # - comments
    # TODO:
    # - detect and remove 'move' operations (whole file deletion and re-creation)
    #   -> look in commit['status'] for 'added' & 'removed'
    # - other non-relevant changes?
    reduced_patch = []
    for line in file_obj['patch'].splitlines():
        if line.startswith('+'):
            line = line[1:].lstrip()
            if line:
                if line[0] == '#':
                    continue
                reduced_patch.append(line)
    #pdebug(reduced_patch, 'Reduced Patch')
    return extract_technology_exposure(reduced_patch, prefixes, date)


def scan_tech_in_contents(api, file_obj, date):
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    python_code = b64decode(api.get(file_obj['contents_url']).data['content'])
    prefixes = extract_prefixes(python_code)
    return extract_technology_exposure(python_code, prefixes, date)


