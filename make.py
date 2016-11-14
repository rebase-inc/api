from collections import namedtuple
from logging import getLogger
from os import getcwd
from os.path import abspath, exists, join
from pprint import pprint
from subprocess import check_call, check_output, call
from sys import argv, exit

from rebase.common.directory import cd
from rebase.common.log import log_to_stdout


logger = getLogger(__name__)


Container = namedtuple('Container', ['tag', 'path'])


common_containers = {
    'build':        Container('rebase/build',           'docker/build'),
    'rsyslog':      Container('rebase/rsyslog',         'docker/rsyslog'),
    'rq_dashboard': Container('rebase/rq_dashboard',    'docker/rq_dashboard'),
    'jupyter':      Container('rebase/jupyter',         'docker/jupyter'),
}


def docker_build(name, container):
    print('Building Docker Container {}'.format(name))
    check_call(['docker', 'build', '-t', container.tag, container.path])


def docker_push(name, container):
    print('Pushing Docker Container {}'.format(name))
    check_call(['docker', 'push', container.tag])


def docker_images(image):
    images_out = check_output(('docker', 'images', '-q', image), universal_newlines=True)
    images = list(filter(lambda line: bool(line), images_out.split('\n')))
    return images


def install_stripper():
    if not exists('../strip-docker-image'):
        with cd('..'):
            check_call(('git', 'clone', 'https://github.com/mvanholsteijn/strip-docker-image'))


def build_java_base_image():
    with cd('../strip-docker-image'):
        check_call((
            './bin/strip-docker-image', '-i', 'openjdk:8-jre', '-t', 'rebase/jre',
            '-p openjdk-8-jre-headless:amd64', 
            '-f', '/etc/passwd',
            '-f', '/usr/lib/jvm/',
            '-f', '/lib/*/libnss*',
            '-f', '/bin/ls',
            '-f', '/bin/cat',
            '-f', '/bin/sh',
            '-f', '/bin/mkdir'
            '-f', '/bin/ps',
            '-f', '/bin/sh',
            '-f', '/var/run',
            '-f', '/run',
        ))


def installed_with_brew(pkg):
    return call(('brew', 'ls', '--versions', pkg)) == 0


def install_java_dev():
    install_stripper()
    if not docker_images('rebase/jre'):
        build_java_base_image()
    if not installed_with_brew('gradle'):
        check_call(('brew', 'install', 'gradle'))


def build_parser_jar():
    with cd('../parser'):
        check_call(('gradle', 'build'))


def build_python_services(*args):
    check_call(('docker', 'volume', 'create', '--name', 'wheelhouse'))
    cwd = getcwd()
    react_app = abspath('../react-app')
    base_args = (
        'docker', 'run', '-it', '--rm',
        '--volume', '/wheelhouse:/wheelhouse:rw',
        '--volume', cwd+':/api',
        '--volume', react_app+':/react-app',
        '--volume', '/var/run/docker.sock:/var/run/docker.sock',
        'rebase/build',
    )
    check_call((*base_args, *args))


def build_react_client():
    with cd('../react-app'):
        check_call(('docker', 'build', '-t', 'rebase/client', '.'))


def build_javascript_parser():
    with cd('../profile-js'):
        check_call(('docker', 'build', '-t', 'rebase/javascript', '.'))


def main(dev=True):
    log_to_stdout()
    logger.debug('==================================')
    logger.debug('Building images for dev mode: {}'.format(dev))
    logger.debug('==================================')
    for name, container in common_containers.items():
        docker_build(name, container)
    install_java_dev()
    build_parser_jar()
    build_javascript_parser()
    if dev:
        check_call(('docker', 'build', '-t', 'rebase/dev-parser', '../parser/docker/parser'))
        build_python_services('docker/build/build-dev')
        build_react_client()
    else:
        check_call((
            'docker',
            'build',
            '-t', 'rebase/pro-parser',
            '-f', '../parser/pro-Dockerfile',
            '../parser/'
        ))
        build_python_services('docker/build/build-pro')


if __name__ == '__main__':
    if len(argv) == 1:
        dev = True
    elif (len(argv) == 2):
        dev = (argv[1] != 'pro')
    else:
        print('Wrong number of arguments:\npython3 -m make [pro]')
        exit(1)
    main(dev=dev)


