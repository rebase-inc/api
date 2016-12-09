from os import getcwd, makedirs
from os.path import abspath, expanduser, join, isdir
from shutil import rmtree, copy, copytree
from subprocess import check_call


def main():
    print('Building docker/nginx/build-pro.py')

    # can't mount a symlinked dir like /tmp
    build_dir=expanduser('~/.rebase/build/nginx')
    www_dir=join(build_dir, 'www')

    if isdir(build_dir):
        rmtree(build_dir)
    makedirs(www_dir)

    code2resume=abspath('../code2resume')

    check_call(('docker', 'build', '-t', 'rebase/code2resume', '../code2resume'))
    check_call(('docker', 'run', '--rm', '-it', '-v', code2resume+':/code', 'rebase/code2resume', '/code/start', 'build'))

    assets_code2resume = join(www_dir, 'assets/code2resume')
    code2resume_build = join(code2resume, 'build')
    makedirs(assets_code2resume)
    copy(
        join(code2resume_build, 'index.html'),
        assets_code2resume
    )
    copytree(
        join(code2resume_build, 'static'),
        join(assets_code2resume, 'static')
    )

    _copy = lambda src, dst: copy(abspath(join('docker', 'nginx', src)), dst)
    _copy('pro-Dockerfile', join(build_dir, 'Dockerfile'))
    _copy('local-pro-Dockerfile', build_dir)
    _copy('nginx.conf', build_dir)
    _copy('default-443.conf', build_dir)
    _copy('default-80.conf', build_dir)
    _copy('nginx-ssl.conf', build_dir)
    _copy('api_proxy.conf', build_dir)
    _copy('api_proxy_local.conf', build_dir)
    _copy('listen.bash', build_dir)

    check_call(('docker', 'build', '-t', 'rebase/pro-nginx', '.'), cwd=build_dir)
    check_call(('docker', 'tag', 'rebase/pro-nginx', 'alpha.rebaseapp.com:5000/rebase/pro-nginx'), cwd=build_dir)
    check_call(('docker', 'build', '-t', 'rebase/local-pro-nginx', '-f', 'local-pro-Dockerfile', '.'), cwd=build_dir)


if __name__ == '__main__':
    main()


