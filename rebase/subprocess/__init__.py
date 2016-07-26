from .json_subprocess import JsonClientSubprocess, JsonServerSubprocess
from .protocol import ClientProtocol, ServerProtocol


def create_json_streaming_subprocess(executable, fifo_dir):
    transport = JsonClientSubprocess(executable, fifo_dir)
    protocol = ClientProtocol(transport)
    return transport, protocol


def create_json_streaming_server(fifo_dir):
    transport = JsonServerSubprocess(fifo_dir)
    protocol = ServerProtocol(transport)
    return transport, protocol


