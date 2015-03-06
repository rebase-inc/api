
from alveare.common.database import DB

class Organization(DB.Model):
    id =        DB.Column(DB.Integer, primary_key=True)
    name =      DB.Column(DB.String)

    projects =  DB.relationship('Project', backref='organization', lazy='joined', cascade="all, delete-orphan", passive_deletes=True)
    managers = DB.relationship('Manager', backref=DB.backref('organization', lazy='joined', uselist=False), cascade='all, delete-orphan', passive_deletes=True, innerjoin=True)

    def __init__(self, name, user):
        from alveare.models import Manager
        self.name = name
        self.managers.append(Manager(user, self)) # you must have at least one manager

    def __repr__(self):
        return '<Organization[id:{}] "{}" >'.format(self.id, self.name)

