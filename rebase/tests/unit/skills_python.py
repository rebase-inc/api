from ast import parse, walk, Import, ImportFrom
from pprint import pprint
from unittest import TestCase

from rebase.skills.python import (
    PythonScanner,
    tech,
)


class Python(TestCase):

    def test_tech(self):
        self.assertEqual( tech('pickle'), 'Python.__standard_library__.pickle')
        self.assertEqual( tech('foobar'), 'Python.__third_party__.foobar')

    def test_std_lib_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('import pickle', 'foo.py', set())
        self.assertIn('Python.__standard_library__.pickle', libs)
        self.assertEqual( libs['Python.__standard_library__.pickle'], ['pickle'])

        libs = scanner.extract_library_bindings('from logging.handlers import SysLogHandler', 'foo.py', set())
        self.assertIn('Python.__standard_library__.logging.handlers.SysLogHandler', libs)
        self.assertEqual(libs['Python.__standard_library__.logging.handlers.SysLogHandler'], ['SysLogHandler'])

    def test_from_3rd_party_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('from foo import bar as yomama', 'sobig.py', set())
        self.assertIn('Python.__third_party__.foo.bar', libs)
        self.assertEqual( libs['Python.__third_party__.foo.bar'], ['yomama'])

    def test_private_module_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('from foo import bar as yomama', 'sobig.py', { 'foo' })
        self.assertFalse(libs)
        libs = scanner.extract_library_bindings('from a.b.c.d import Foo as Fooyass', 'sobig.py', { 'a.b.c.d' })
        self.assertFalse(libs)

    def test_relative_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('from .foo import bar as yomama', 'sobig.py', set())
        self.assertFalse(libs)


