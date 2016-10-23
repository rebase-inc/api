from ast import parse, walk, Import, ImportFrom
from pprint import pprint
from unittest import TestCase

from ...skills.python import  PythonScanner, tech
from ...skills.py2_py3_scanner import Py2Scanner


class Python(TestCase):

    def test_tech(self):
        self.assertEqual( tech('pickle'), 'Python.__std_library__.pickle')
        self.assertEqual( tech('foobar'), 'Python.__3rd_party__.foobar')

    def test_std_lib_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('import pickle', 'foo.py', [[],[]])
        self.assertIn('Python.__std_library__.pickle', libs)
        self.assertEqual( libs['Python.__std_library__.pickle'], ['pickle'])

        libs = scanner.extract_library_bindings('from logging.handlers import SysLogHandler', 'foo.py', [[],[]])
        self.assertIn('Python.__std_library__.logging.handlers.SysLogHandler', libs)
        self.assertEqual(libs['Python.__std_library__.logging.handlers.SysLogHandler'], ['SysLogHandler'])

    def test_from_3rd_party_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('from foo import bar as yomama', 'sobig.py', [[],[]])
        self.assertIn('Python.__3rd_party__.foo.bar', libs)
        self.assertEqual( libs['Python.__3rd_party__.foo.bar'], ['yomama'])

    def test_private_module_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('from foo import bar as yomama', 'sobig.py', [['foo'],[]])
        self.assertFalse(libs)
        libs = scanner.extract_library_bindings('from a.b.c.d import Foo as Fooyass', 'sobig.py', [['a.b.c.d'],[]])
        self.assertFalse(libs)

    def test_relative_import(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('from .foo import bar as yomama', 'sobig.py', [[],[]])
        self.assertFalse(libs)

    def test_py2_scanner(self):
        scanner = Py2Scanner()
        profile = scanner.scan_contents('foo.py', 'import pickle', 1234, [[],[]])
        self.assertIn('Python.__std_library__.pickle', profile)
        self.assertEqual( profile['Python.__std_library__.pickle'].first, 1234)
        self.assertEqual( profile['Python.__std_library__.pickle'].last, 1234)
        self.assertEqual( profile['Python.__std_library__.pickle'].total_reps, 1)
        profile = scanner.scan_contents('sobig.py', 'from a.b.c.d import Foo as Fooyass', 1234, [['a.b.c.d'],[]])
        std_lib_keys = 0
        third_party_lib_keys = 0
        for tech, exposure in profile.items():
            if tech.startswith('Python.__std_library__'):
                std_lib_keys += 1
            elif tech.startswith('Python.__3rd_party__'):
                third_party_lib_keys += 1
        self.assertEqual( std_lib_keys, 0 )
        self.assertEqual( third_party_lib_keys, 0 )
        scanner.close()


