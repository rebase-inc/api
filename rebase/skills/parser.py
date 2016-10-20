from logging import getLogger

from rebase.common.debug import pdebug
from rebase.skills.socket_rpc_client import SocketRPCClient, method
from rebase.skills.tech_profile import Exposure, TechProfile, to_TechProfile_or_Exposure
from rebase.skills.technology_scanner import TechnologyScanner


logger = getLogger(__name__)


class Client(SocketRPCClient):

    languages = method(0)

    grammar_rules = method(1) 

    scan_contents = method(2)

    scan_patch = method(3)


class Parser(TechnologyScanner):

    def __init__(self, language, host='parser', port=1111):
        self.client = Client(host, port)
        self.languages_ = self.client.languages()
        if language not in self.languages_:
            raise Exception('Language "{}" is not supported'.format(language))
        self.language = language
        self.language_index = self.languages_.index(self.language)

    def languages(self):
        return self.client.languages()

    def grammar_rules(self):
        return self.client.grammar_rules(self.language_index)

    def scan_contents(self, filename, code, date, context):
        use = self.client.scan_contents(self.language_index, code)
        return TechProfile({ rule: Exposure(date, date, reps) for rule, reps in use.items() })

    def scan_patch(self, filename, code, previous_code, patch, date, context):
        use = self.client.scan_patch(self.language_index, code, previous_code, patch)
        return TechProfile({ rule: Exposure(date, date, reps) for rule, reps in use.items() })


