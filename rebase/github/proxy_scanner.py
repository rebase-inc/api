from logging import getLogger

from rebase.skills.technology_scanner import TechnologyScanner
from rebase.skills.tech_profile import TechProfile, Exposure
from rebase.subprocess import create_json_streaming_subprocess


logger = getLogger(__name__)


def to_TechProfile_or_Exposure(dct):
    '''
        JSON deserialization transforms dict keys into strings by default
        This rebuilds a TechProfile or a Exposure from a dict
    '''
    if ('first' in dct) and ('last' in dct) and ('total_reps' in dct):
        return Exposure(dct['first'], dct['last'], dct['total_reps'])
    else:
        return TechProfile(dct)


class Proxy(TechnologyScanner):
    '''
        A proxy scanner for any language (python, javascript, etc.)
    '''

    def __init__(self, executable_path, fifo_dir):
        self.transport, self.protocol = create_json_streaming_subprocess(
            executable_path,
            fifo_dir, 
            loads_kwargs={ 'object_hook': to_TechProfile_or_Exposure }
        )
        self.scan_patch_call = {
            'method':   'scan_patch',
            'args':     None
        }
        self.scan_contents_call = {
            'method':   'scan_contents',
            'args':     None
        }

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

    def scan_patch(self, *args):
        self.scan_patch_call['args'] = args
        self.protocol.write_in(self.scan_patch_call)
        return self.get_results()

    def scan_contents(self, *args):
        self.scan_contents_call['args'] = args
        self.protocol.write_in(self.scan_contents_call)
        return self.get_results()

    def close(self):
        self.transport.close()


