from ast import parse, walk, Import, ImportFrom
from base64 import b64decode
from datetime import datetime, timedelta

from rebase.common.debug import pdebug


def scan_tech_in_commit(api, file_obj, date):
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    language = 'Python.'
    python_code = b64decode(api.get(file_obj['contents_url']).data['content'])
    tree = parse(python_code, 'string')
    # prefixes is a dictionary where a key is a sub-component of a techs 
    # (e.g. 'sqlalchemy.orm') and the value is a list of prefixes (['sa', 'sqlalchemy.orm'])
    # prefixes is thus a collection of search keywords to be applied on the commit patches
    prefixes = defaultdict(list)
    for node in walk(tree):
        if isinstance(node, Import):
            for _alias in node.names:
                if _alias.asname:
                    prefixes[_alias.name].append(_alias.asname)
                prefixes[language+_alias.name].append(_alias.name)
        if isinstance(node, ImportFrom):
            for _alias in node.names:
                sub_component = node.module+'.'+_alias.name
                prefixes[language+sub_component].append(_alias.asname if _alias.asname else _alias.name)
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
    exposure = defaultdict(list)
    for component, keywords in prefixes.items():
        for prefix in keywords:
            for line in reduced_patch:
                if prefix in line:
                    exposure[component].append(date)
    #pdebug(exposure, 'Technology Exposure')
    return exposure


