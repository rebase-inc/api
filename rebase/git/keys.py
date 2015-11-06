from subprocess import check_call

from rebase import create_app
from rebase.models.ssh_key import SSHKey


one_line = 'command="filter {user_id} $SSH_ORIGIINAL_COMMAND" {key}\n'.format
destination = 'git@{host}:{path}'.format

def generate_authorized_keys():
    app, _, _ = create_app()
    tmp_keys = app.config['TMP_KEYS']
    with open(tmp_keys, 'w') as authorized_keys:
        for ssh_key in SSHKey.query.all():
            authorized_keys.write(one_line(user_id=ssh_key.user.id, key=ssh_key.key))
    check_call(['scp', tmp_keys, destination(host=app.config['WORK_REPOS_HOST'], path=app.config['SSH_AUTHORIZED_KEYS']) ])
