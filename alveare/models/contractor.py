from sqlalchemy.orm import validates

from alveare.models.role import Role
from alveare.models.user import User
from alveare.common.database import DB

class Contractor(Role):
    id = DB.Column(DB.Integer, DB.ForeignKey('role.id'), primary_key=True)
    busyness = DB.Column(DB.Integer, nullable=False)
    skill_set = DB.relationship('SkillSet', backref='contractor', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    remote_work_history = DB.relationship('RemoteWorkHistory', uselist=False, backref='contractor', cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = { 'polymorphic_identity': 'contractor' }

    def __init__(self, user):
        if not isinstance(user, User):
            raise ValueError('{} field on {} must be {} not {}'.format('user', self.__tablename__, User, type(user)))
        self.user = user
        self.busyness = 1

    def __repr__(self):
        return '<Contractor[id:{}] busyness="{}">'.format(self.id, self.busyness)
