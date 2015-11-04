from subprocess import check_call

from rebase import create_app
from rebase.models.ssh_key import SSHKey


one_line = 'environment="REBASE_USER={user_id}" {key}\n'.format
destination = '{host}:{path}'.format

def generate_authorized_keys():
    app, _, _ = create_app()
    tmp_keys = app.config['TMP_KEYS']
    with open(tmp_keys, 'w') as authorized_keys:
        for ssh_key in SSHKey.query.all():
            authorized_keys.write(one_line(ssh_key.user.id, ssh_key.key))
    check_call(['scp', tmp_keys, destination(app.config['WORK_REPOS_HOST'], app.config['SSH_AUTHORIZED_KEYS']) ])
