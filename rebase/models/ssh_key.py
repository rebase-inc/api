from hashlib import md5
from os import remove
from subprocess import check_output

from rebase.common.database import DB, PermissionMixin

class SSHKey(DB.Model, PermissionMixin):
    __pluralname__ = 'ssh_keys'

    id =            DB.Column(DB.Integer, primary_key=True)
    user_id =       DB.Column(DB.Integer, DB.ForeignKey('user.id', ondelete='CASCADE'))
    title =         DB.Column(DB.String, nullable=False)
    key =           DB.Column(DB.String, nullable=False)
    fingerprint =   DB.Column(DB.String, nullable=False)

    def __init__(self, user, title, key):
        ''' 
        user: a User object.
        title: a way to annotate your key.
        key: the key itself.
        '''
        self.user = user
        self.title = title
        self.key = key
        self.fingerprint = get_fingerprint(self.key)

    def query_by_user(user):
        if user.is_admin():
            return SSHKey.query
        return SSHKey.query.filter(SSHKey.user==user)

    def allowed_to_be_created_by(self, user):
        return self.user == user

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return user.is_admin() or self.user == user

    def __repr__(self):
        return '<SSHKey[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = cls.as_manager_path = []

def get_fingerprint(key):
    # could not get paramiko PKey to work just yet, so reverting to straight 
    # subprocess calls...
    key_path = '/tmp/rebase-key-'+md5(key.encode('utf-8')).hexdigest()
    with open(key_path, 'w') as f:
        f.write(key)
    _fingerprint =  check_output(['ssh-keygen', '-l', '-f', key_path])
    remove(key_path)
    return _fingerprint.decode('utf-8')
