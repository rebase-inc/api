from .json_subprocess import JsonClientSubprocess, JsonServerSubprocess
from .protocol import ClientProtocol, ServerProtocol


def create_json_streaming_subprocess(executable, fifo_dir, dumps_kwargs=dict(), loads_kwargs=dict()):
    transport = JsonClientSubprocess(executable, fifo_dir, dumps_kwargs, loads_kwargs)
    protocol = ClientProtocol(transport)
    return transport, protocol


def create_json_streaming_server(fifo_dir, dumps_kwargs=dict(), loads_kwargs=dict()):
    transport = JsonServerSubprocess(fifo_dir, dumps_kwargs, loads_kwargs)
    protocol = ServerProtocol(transport)
    return transport, protocol


