from pprint import pprint
from unittest import TestCase

from ....skills.remote_scanner_client import RemoteScannerClient
from ....skills.javascript import Javascript


class JS(TestCase):

    def test_client_languages(self):
        client = RemoteScannerClient('javascript', 7777)
        languages = client.languages()
        client.close()
        self.assertIn('Javascript', languages)
        self.assertEqual(languages.index('Javascript'), 0)

    def test_client_grammar(self):
        client = RemoteScannerClient('javascript', 7777)
        grammar = client.grammar()
        client.close()
        self.assertIn('ExpressionStatement', grammar)
        self.assertIn('CatchClause', grammar)
        self.assertIn('WhileStatement', grammar)
        self.assertIn('JSXExpressionContainer', grammar)

    def test_client_scan_contents(self):
        with open('./rebase/tests/unit/skills/protocol.js') as protocol_js:
            code = protocol_js.read()
        client = RemoteScannerClient('javascript', 7777)
        profile = client.scan_contents(0, 'protocol.js', code, None)
        client.close()
        self.assertIn('1.Map', profile)
        self.assertIn('0.SwitchStatement', profile)

    def parse(self, filename):
        with open(filename) as protocol_js:
            code = protocol_js.read()
        scanner = Javascript()
        profile = scanner.scan_contents(filename, code, 1234, None)
        scanner.close()
        return profile

    def test_scan_contents(self):
        profile = self.parse('./rebase/tests/unit/skills/protocol.js')
        self.assertIn('Javascript.1.Map', profile)
        self.assertIn('Javascript.0.SwitchStatement', profile)

    def test_SingleContractView(self):
        profile = self.parse('./rebase/tests/unit/skills/SingleContractView.react.js')
        pprint(profile)
