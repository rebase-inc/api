from base64 import b64encode
from json import JSONEncoder
from logging import getLogger

from .importable_modules import ImportableModules
from .scanner_client import ScannerClient
from ..subprocess import create_json_streaming_subprocess


logger = getLogger(__name__)


class Encoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ImportableModules):
            return tuple(obj)
        return obj


class Proxy(ScannerClient):
    '''
        A proxy scanner for any language (python, javascript, etc.)
    '''

    def __init__(self, executable_args, fifo_dir):
        self.transport, self.protocol = create_json_streaming_subprocess(
            executable_args,
            fifo_dir, 
            dumps_kwargs={ 'cls': Encoder },
        )
        self.languages_call = {
            'method':   'languages',
            'args':     None
        }
        self.grammar_call = {
            'method':   'grammar',
            'args':     None
        }
        self.scan_contents_call = {
            'method':   'scan_contents',
            'args':     None
        }
        super().__init__()

    def get_results(self):
        err = self.protocol.read_err()
        if err:
            self.protocol.read_out()
            number, value = err
            if number == 0:
                se = SyntaxError()
                se.filename = value['filename']
                se.lineno = value['lineno']
                se.offset = value['offset']
                se.text = value['text']
                raise se
            else:
                raise Exception(value)
        return self.protocol.read_out()

    def languages(self):
        self.protocol.write_in(self.languages_call)
        return self.get_results()

    def grammar(self, *args):
        self.grammar_call['args'] = args
        self.protocol.write_in(self.grammar_call)
        return self.get_results()

    def scan_contents(self, language_index, filename, code, context):
        self.scan_contents_call['args'] = [language_index, filename, b64encode(code).decode(), context]
        self.protocol.write_in(self.scan_contents_call)
        return self.get_results()

    def close(self):
        self.transport.close()


