
from alveare.common.database import DB

class Organization(DB.Model):
    id =        DB.Column(DB.Integer, primary_key=True)
    name =      DB.Column(DB.String)

    projects =  DB.relationship('Project', backref='organization', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Organization[id:{}] "{}" >'.format(self.id, self.name)

