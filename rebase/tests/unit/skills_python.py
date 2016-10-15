from unittest import TestCase

from rebase.skills.python import tech, PythonScanner


class Python(TestCase):

    def test_tech(self):
        self.assertEqual( tech('pickle'), 'Python.__standard_library__.pickle')
        self.assertEqual( tech('foobar'), 'Python.__third_party__.foobar')

    def test_libs(self):
        scanner = PythonScanner()
        libs = scanner.extract_library_bindings('import pickle', 'foo.py')
        self.assertIn('Python.__standard_library__.pickle', libs)
        self.assertEqual( libs['Python.__standard_library__.pickle'], ['pickle'])

        libs = scanner.extract_library_bindings('from foo import bar as yomama', 'sobig.py')
        self.assertIn('Python.__third_party__.foo.bar', libs)
        self.assertEqual( libs['Python.__third_party__.foo.bar'], ['yomama'])


