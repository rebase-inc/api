
from .scanner_client import ScannerClient
from .socket_rpc_client import SocketRPCClient, method

PORT = 25000

class TechnologyImpactService(SocketRPCClient):

    def __init__(self, host, port = PORT):
        SocketRPCClient.__init__(self, host, port)

    get_impact = method(0)
