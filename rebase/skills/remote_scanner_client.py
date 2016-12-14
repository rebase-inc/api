from base64 import b64encode

from .scanner_client import ScannerClient
from .socket_rpc_client import SocketRPCClient, method


class RemoteScannerClient(SocketRPCClient, ScannerClient):

    def __init__(self, host, port):
        SocketRPCClient.__init__(self, host, port)
        ScannerClient.__init__(self)

    close = SocketRPCClient.close

    languages = method(0)

    grammar = method(1) 

    def scan_contents(self, language_index, filename, code, context):
        return super().remote_procedure_call(
            2,
            language_index,
            filename,
            b64encode(code).decode(),
            context
        )


