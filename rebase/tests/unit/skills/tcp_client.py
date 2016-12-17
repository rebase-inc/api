from pprint import pprint
from unittest import TestCase

from ....skills.remote_scanner_client import TCPClient

foo_java='''
import static java.io.out;

class Foo {
    static { out.println("bar"); }
}

'''

class TCPClientTest(TestCase):

    def test_languages(self):
        client = TCPClient('parser', 1111)
        languages = client.languages()
        client.close()
        self.assertIn('Java', languages)
        self.assertEqual(languages.index('Java'), 0)
        
    def test_grammar(self):
        client = TCPClient('parser', 1111)
        grammar_rules = client.grammar(0)
        client.close()
        self.assertIn('ClassOrInterfaceType', grammar_rules)

    def test_scan_contents(self):
        client = TCPClient('parser', 1111)
        profile = client.scan_contents(0, 'foo.java', foo_java, '')
        client.close()
        self.assertIn('Java.__std_library__.java.io.out.println', profile)


