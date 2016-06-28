#!/usr/bin/env python3

from collections import namedtuple
from subprocess import check_call

Container = namedtuple('Container', ['tag', 'path'])

containers = {
    'api':          Container('rebase/api',             '.'),
    'rq_git':       Container('rebase/rq_git',          'docker/git'),
    'rsyslog':      Container('rebase/rsyslog',         'docker/rsyslog'),
    'client':       Container('rebase/client',          '../react-app'),
    'rq_dashboard': Container('rebase/rq_dashboard',    'docker/git'),
    #'letsencrypt':  Container('rebase/letsencrypt',    'docker/letsencrypt'),
    'nginx':        Container('rebase/nginx',           'docker/nginx'),
}

def docker_build(name, container):
    print('Building Docker Container {}'.format(name))
    check_call(['docker', 'build', '-t', container.tag, container.path])


def docker_push(name, container):
    print('Pushing Docker Container {}'.format(name))
    check_call(['docker', 'push', container.tag])


if __name__ == '__main__':
    for name, container in containers.items():
        docker_build(name, container)
    for name, container in containers.items():
        docker_push(name, container)
