from subprocess import call, check_call

class SSH(object):
    def __init__(self, user, host):
        self.user = user
        self.host = host
        self.prefix_args = ('ssh', self.user+'@'+self.host)

    def __call__(self, cmd, check=True, **kwargs):
        _cmd = list(self.prefix_args)
        _cmd.extend(cmd)
        print('Executing: {}'.format(_cmd))
        if check:
            check_call(_cmd, **kwargs)
        else:
            return call(_cmd, **kwargs)
