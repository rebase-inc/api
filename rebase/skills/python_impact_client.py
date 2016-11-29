
from .scanner_client import ScannerClient
from .socket_rpc_client import SocketRPCClient, method


class TechnologyImpactService(SocketRPCClient):

    def __init__(self, host, port):
        SocketRPCClient.__init__(self, host, port)

    get_impact = method(0)
