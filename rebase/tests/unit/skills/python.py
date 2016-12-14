from ast import parse, walk, Import, ImportFrom
from functools import partialmethod
from pprint import pprint
from unittest import TestCase

from ....skills.importable_modules import ImportableModules
from ....skills.python import Python
from ....skills.python_client import PythonClient, tech
from ....skills.py2_client import Py2Client
from ....skills.py2_py3_client import Py2Py3Client

from .git import Tree, Blob, Commit


code_1 = b'''
from pickle import loads, dumps
from aws.s3 import S3
from a.b import Foo

s3 = S3()

s3.put('foo', dumps({1:2, 3:4}))

'''

code_2 = b'''
from pickle import dumps
from aws.s3 import S3
from a.b import Foo

s3 = S3()

s3.put('foo', dumps({1:2, 3:4}))

foo = Foo()

'''


class PythonTest(TestCase):

    def scanner_client(self, Client):
        client0 = Client()
        client0.close()
        client = Client()
        self.assertEqual( list(client.languages()), ['Python'])
        technologies = client.scan_contents(0, 'foo.py', code_1, ImportableModules())
        client.close()
        S3_key = '2.aws.s3.S3'
        loads_key = '1.pickle.loads'
        dumps_key = '1.pickle.dumps'
        self.assertIn(loads_key, technologies)
        self.assertEqual(technologies[loads_key], 1)
        self.assertIn(dumps_key, technologies)
        self.assertEqual(technologies[dumps_key], 2)
        self.assertIn(S3_key, technologies)
        self.assertEqual(technologies[S3_key], 2)

    test_python_client = partialmethod(scanner_client, PythonClient)

    test_py2_client = partialmethod(scanner_client, Py2Client)

    test_py2_py3_client = partialmethod(scanner_client, Py2Py3Client)

    def test_scan_diff(self):
        Foo_py = Blob('Foo.py', 'a/b/Foo.py', contents=code_1)
        b_init_py = Blob('__init__.py', 'a/b/__init__.py')
        b = Tree('b', 'a/b', blobs=[b_init_py, Foo_py])
        a_init_py = Blob('__init__.py', 'a/__init__.py')
        a = Tree('a', 'a', blobs=[a_init_py], trees=[b])
        parent_commit = Commit(a)

        Foo_py_2 = Blob('Foo.py', 'a/b/Foo.py', contents=code_2)
        b_2 = Tree('b', 'a/b', blobs=[b_init_py, Foo_py_2])
        a_2 = Tree('a', 'a', blobs=[a_init_py], trees=[b_2])
        commit = Commit(a_2)

        scanner = Python()
        tech_profile = scanner.scan_diff(
            Foo_py_2.name,
            Foo_py_2.contents,
            commit,
            Foo_py.contents,
            parent_commit,
            1234
        )
        scanner.close()
        self.assertNotIn('Python.2.a.b.Foo', tech_profile)


