
from .scanner_client import ScannerClient
from .socket_rpc_client import SocketRPCClient, method


class RemoteScannerClient(SocketRPCClient, ScannerClient):

    def __init__(self, host, port):
        SocketRPCClient.__init__(self, host, port)
        ScannerClient.__init__(self)

    languages = method(0)

    grammar = method(1) 

    scan_contents = method(2)

    close = SocketRPCClient.close


