from rebase.models.ssh_key import SSHKey

tmp_keys='/tmp/authorized_keys'

def generate_authorized_keys():
    from rebase import create_app
    app, _, db = create_app()
    with open(tmp_keys, 'w') as authorized_keys:
        keys = SSHKey.query.all()
        for ssh_key in keys:
            line = 'environment="REBASE_USER={user_id}" {key}\n'.format(
                user_id=ssh_key.user.id,
                key=ssh_key.key
            )
            authorized_keys.write(line)
