from pprint import pprint
from unittest import TestCase

from git import Repo

from rebase.skills.importable_modules import (
    ImportableModules,
    is_python_module,
    path_without_extension,
    python_modules,
    start_dir,
    to_namespace,
)


def Blob(name, path):
    return type('_Blob', (object,), { 'path': path, 'name': name })


def Tree(name, path, blobs=None, trees=None):
    return type('_Tree', (object,), {
        'name': name,
        'path': path,
        'blobs': blobs or list(),
        'trees': trees or list()
    })


class ImportableModulesTest(TestCase):

    def test_is_python_module(self):
        foo_py = Blob('foo.py', 'x/y/z/foo.py')
        bar_js = Blob('bar.js', 'a/b/c/bar.js')
        self.assertTrue( is_python_module(foo_py) )
        self.assertFalse( is_python_module(bar_js) )

    def test_path_without_extension(self):
        foo_py = Blob('foo.py', 'a/b/c/foo.py')
        self.assertEqual( path_without_extension(foo_py), 'a/b/c/foo' )

    def test_python_modules(self):
        foo_py = Blob('foo.py', 'a/b/c/foo.py')
        yo_py = Blob('yo.py', 'a/b/c/yo.py')
        bar_js = Blob('bar.js', 'a/b/c/bar.js')
        tree = Tree('c', 'a/b/c', blobs=[ foo_py, yo_py, bar_js ])
        self.assertEqual( python_modules(tree), { 'a/b/c/foo', 'a/b/c/yo' } )

    def test_to_namespace(self):
        self.assertEqual( to_namespace('a/b', 'a'), 'b' )
        self.assertEqual( to_namespace('a/b/c/foo', 'a/b'), 'c.foo' )
        self.assertEqual( to_namespace('a/b/c/foo', ''), 'a.b.c.foo' )

    def test_start_dir(self):
        self.assertEqual( start_dir('a'), '')
        self.assertEqual( start_dir('a/b'), 'a')
        self.assertEqual( start_dir('a/b/c'), 'a/b')

    def test_importable_modules_root_modules(self):
        foo_py = Blob('foo.py', 'foo.py')
        yo_py = Blob('yo.py', 'yo.py')
        bar_js = Blob('bar.js', 'bar.js')
        tree = Tree('', '', blobs=[ foo_py, yo_py, bar_js ])
        importable_modules = ImportableModules(tree)
        self.assertEqual( importable_modules, { 'foo', 'yo' } )

    def test_importable_modules_one_sub_dir(self):
        foo_py = Blob('foo.py', 'a/foo.py')
        yo_py = Blob('yo.py', 'a/yo.py')
        bar_js = Blob('bar.js', 'a/bar.js')
        a = Tree('a', 'a', blobs=[foo_py, yo_py, bar_js])
        root_tree = Tree('', '', trees=[a])
        importable_modules = ImportableModules(root_tree)
        self.assertEqual( importable_modules, { 'foo', 'yo' } )

    def test_importable_modules_one_pkg(self):
        b = Tree('b', 'a/b', blobs=[
            Blob('__init__.py', 'a/b/__init__.py'),
            Blob('foo.py',      'a/b/foo.py'),
            Blob('yo.py',       'a/b/yo.py'),
            Blob('bar.js',      'a/b/bar.js'),
        ])
        a = Tree('a', 'a', blobs=[Blob('__init__.py', 'a/__init__.py')], trees=[b])
        root_tree = Tree('', '', trees=[a])
        importable_modules = ImportableModules(root_tree)
        self.assertEqual( importable_modules, { 'a', 'a.b', 'a.b.foo', 'a.b.yo' } )

    def test_modules(self):
        backend = Repo('.')
        commit = backend.commit('d4819c15b3994dcd9e5faed9f180f1eaa71e3210')
        importable_modules = ImportableModules(commit.tree)
        root_modules = {'build', 'git-worker', 'parse_python2', 'rq-population', 'run-worker', 'scheduler', 'wsgi'}
        self.assertTrue(root_modules.issubset(importable_modules))
        

