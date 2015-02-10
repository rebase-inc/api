
from alveare.common.database import DB

class User(DB.Model):

    id =                DB.Column(DB.Integer,   primary_key=True)
    first_name =        DB.Column(DB.String,    nullable=False)
    last_name =         DB.Column(DB.String,    nullable=False)
    email =             DB.Column(DB.String,    nullable=False)
    hashed_password =   DB.Column(DB.String,    nullable=False)
    last_seen =         DB.Column(DB.DateTime,  nullable=False)

    def __init__(self, first_name, last_name, email, hashed_password, last_seen):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = hashed_password
        self.last_seen = last_seen

    def __repr__(self):
        return '<User[id:{}] first_name={} last_name={} email={}>'.format(self.id, self.first_name, self.last_name, self.email)

