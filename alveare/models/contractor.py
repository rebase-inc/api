from sqlalchemy.ext.hybrid import hybrid_property

from alveare.models.role import Role
from alveare.models.user import User
from alveare.common.database import DB, PermissionMixin

class Contractor(Role):
    __pluralname__ = 'contractors'

    id =            DB.Column(DB.Integer, DB.ForeignKey('role.id'), primary_key=True)
    busyness =      DB.Column(DB.Integer, nullable=False, default=1)

    clearances =          DB.relationship('CodeClearance',     backref='contractor', cascade='all, delete-orphan', passive_deletes=True)
    skill_set =           DB.relationship('SkillSet',          uselist=False, backref='contractor', cascade='all, delete-orphan', passive_deletes=True)
    remote_work_history = DB.relationship('RemoteWorkHistory', uselist=False, backref='contractor', cascade='all, delete-orphan', passive_deletes=True)
    auction_nominations = DB.relationship('Nomination',        backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)
    bank_account =        DB.relationship('BankAccount',       backref='contractor', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    work_offers =         DB.relationship('WorkOffer',         backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)
    bids =                DB.relationship('Bid',               backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)
    feedbacks =           DB.relationship('Feedback',          backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = { 'polymorphic_identity': 'contractor' }

    def __init__(self, user):
        if not isinstance(user, User):
            raise ValueError('{} field on {} must be {} not {}'.format('user', self.__tablename__, User, type(user)))
        self.user = user
        self.busyness = 1

    @hybrid_property
    def auctions_approved_for(self):
        auctions_approved_for = []
        for nomination in self.auction_nominations:
            approved = nomination.auction
            if approved:
                auctions_approved_for.append(approved.id)
        return auctions_approved_for

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    def __repr__(self):
        return '<Contractor[id:{}] busyness="{}">'.format(self.id, self.busyness)
