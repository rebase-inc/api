

def is_python_module(blob):
    return blob.path.endswith('.py')


def path_without_extension(blob):
    '''

        "a/b/c/foo.py" => "a/b/c/foo"

    '''
    return blob.path[:blob.path.rfind('.py')]


def python_modules(tree):
    '''
    tree = {
            name: 'c',
            blobs:  [
                        { path: 'a/b/c/foo.py'  },
                        { path: 'a/b/c/bar.py'  },
                        { path: 'a/b/c/yo.js'   },
                    ]
    }

    python_modules(tree) => { 'a/b/c/foo', 'a/b/c/bar' }

    '''
    return set( path_without_extension(blob) for blob in tree.blobs if is_python_module(blob) )


def to_namespace(path, start_directory=''):
    '''

        to_namespace('a/b/c/foo', 'a/b') => 'c.foo'

    '''
    if path.find(start_directory) != 0:
        raise ValueError('to_namespace could not locate prefix {} in {}'.format(start_directory, path))
    start = len(start_directory)+1 if start_directory else 0
    return path[start:].replace('/', '.')


def to_namespaces(modules, start_directory):
    return set( to_namespace(module, start_directory=start_directory) for module in modules )


def start_dir(pkg_path):
    return '/'.join(pkg_path.split('/')[:-1])


class ImportableModules(frozenset):

    def __new__(cls, tree_root=None):
        namespaces = set()
        q = [ (tree_root, None) ] if tree_root else None
        while q:
            tree, start_directory = q.pop()
            modules = python_modules(tree) or set()
            if tree.path+'/'+'__init__' in modules:
                ImportableModules.pkg_detected(cls, q, namespaces, tree, start_directory, modules)
            elif not start_directory:
                namespaces |= to_namespaces(modules, tree.path)
                q.extend( (subtree, None) for subtree in tree.trees )
        return super(ImportableModules, cls).__new__(cls, namespaces)

    def pkg_detected(cls, q, namespaces, tree, start_directory, modules):
        '''

        Mark 'tree' as a pkg, enqueues its modules and sub-directories.
        Detect the start_directory because the namespace only starts
        at the first __init__.py encountered in a pkg tree.

        For example, with:
        'foo/bar/zoo/__init__.py' => start_directory = 'foo/bar'

        '''
        start_directory = start_directory if start_directory is not None else start_dir(tree.path)
        pkg_ns = to_namespace(tree.path, start_directory)
        namespaces.add(pkg_ns)
        namespaces |= set( to_namespace(module, start_directory=start_directory) for module in modules if not module.endswith('__init__'))
        q.extend( (subtree, start_directory) for subtree in tree.trees )


