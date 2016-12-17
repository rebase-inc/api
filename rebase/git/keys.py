from subprocess import check_call

from rebase.app import create
from rebase.models.ssh_key import SSHKey


one_line = 'command="filter {user_id} $SSH_ORIGINAL_COMMAND" {key}\n'.format

def generate_authorized_keys():
    app = create()
    with app.app_context():
        with open(app.config['SSH_AUTHORIZED_KEYS'], 'w') as authorized_keys:
            for ssh_key in SSHKey.query.all():
                authorized_keys.write(one_line(user_id=ssh_key.user.id, key=ssh_key.key))
