from alveare.common.database import DB

class Role(DB.Model):
    __pluralname__ = 'roles'

    id =      DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    type =    DB.Column(DB.String)

    __mapper_args__ = {
        'polymorphic_identity': 'role',
        'polymorphic_on': type
    }

    def __init__(self):
        raise NotImplemented()

    def __repr__(self):
        return '<User[id:{}] first_name={} last_name={} email={}>'.format(self.id, self.first_name, self.last_name, self.email)
