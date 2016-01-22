from functools import partialmethod
from logging import debug, info
from pickle import loads
from queue import Queue
import re

from rebase.cache.base_request import CacheBaseHandler
from rebase.cache.tasks import warmup, cooldown, invalidate


class RoleResource(object):
    path = re.compile(r'/role/(?P<role_id>[0-9]+)')

    def destination(request, match):
        return int(match.group('role_id'))

    def warmup_args(request, match):
        return tuple(), dict()

    def cooldown_args(request, match):
        return tuple(), dict()

    POST = (warmup, warmup_args)
    DELETE = (cooldown, cooldown_args)


class InvalidateResource(object):
    path = re.compile(r'/invalidate')

    def destination(request, match):
        # broadcast to all children
        return 0

    def invalidate_args(request, match):
        changeset = loads(request.rfile.read(int(request.headers['Content-Length'])))
        return (changeset,), dict()

    POST = (invalidate, invalidate_args)


class CacheHandler(CacheBaseHandler):
    # q is used to send tasks to the main thread
    q = Queue()
    all_resources = (RoleResource, InvalidateResource)

    def _handle(self, verb):
        match = None
        matching_resource = None
        for resource in self.all_resources:
            if hasattr(resource, verb):
                match = resource.path.match(self.path)
                if match:
                    matching_resource = resource
                    break
        if match:
            self.send_response(200)
            self.end_headers()
            function, extract_args = getattr(matching_resource, verb)
            args, kwargs = extract_args(self, match)
            task = {
                'id': matching_resource.destination(self, match),
                'action': (function, args, kwargs)
            }
            debug('Sending {} to main thread'.format(task))
            self.q.put(task)
        else:
            self.send_response(404)
            self.end_headers()

    do_POST =   partialmethod(_handle, verb='POST')
    do_DELETE = partialmethod(_handle, verb='DELETE')
