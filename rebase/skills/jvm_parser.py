from logging import getLogger

from .remote_scanner_client import RemoteScannerClient
from .tech_profile import Exposure, TechProfile
from .technology_scanner import TechnologyScanner


logger = getLogger(__name__)


class JVMParser(TechnologyScanner):

    def __init__(self, language, host='parser', port=1111):
        super().__init__(language, RemoteScannerClient(host, port))


