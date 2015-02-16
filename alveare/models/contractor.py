
from alveare.common.database import DB

class Contractor(DB.Model):

    id =            DB.Column(DB.Integer, primary_key=True)
    busyness =      DB.Column(DB.Integer, nullable=False, default=1)
    first_name =    DB.Column(DB.String, nullable=False)
    last_name =     DB.Column(DB.String, nullable=False)
    email =         DB.Column(DB.String, nullable=False)
    
    skill_set =             DB.relationship('SkillSet',             uselist=False, backref='contractor', cascade='all, delete-orphan', passive_deletes=True)
    remote_work_history =   DB.relationship('RemoteWorkHistory',    uselist=False, backref='contractor', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, first_name, last_name, email, skill_set):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.skill_set = skill_set

    def __repr__(self):
        return '<Contractor[id:{}] busyness="{}">'.format(self.id, self.busyness)
