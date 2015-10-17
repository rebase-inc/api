from rebase.common.database import DB, PermissionMixin

class Ticket(DB.Model, PermissionMixin):
    __pluralname__ = 'tickets'

    id =            DB.Column(DB.Integer, primary_key=True)
    created =       DB.Column(DB.DateTime, nullable=False)
    title =         DB.Column(DB.String, nullable=False)
    project_id =    DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    discriminator = DB.Column(DB.String)

    skill_requirement =     DB.relationship('SkillRequirement',     backref='ticket', cascade='all, delete-orphan', passive_deletes=False, uselist=False)
    snapshots =             DB.relationship('TicketSnapshot',       backref='ticket', cascade='all, delete-orphan', passive_deletes=False)
    comments =              DB.relationship('Comment', lazy='joined', backref='ticket', cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'ticket',
        'polymorphic_on': discriminator
    }

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('Ticket is abstract')

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = [
            models.Project,
            models.CodeClearance,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.Project,
            models.Manager,
        ]

        cls.as_owner_path = cls.as_manager_path

    def allowed_to_be_created_by(self, user):
        return self.project.allowed_to_be_modified_by(user)

    def allowed_to_be_modified_by(self, user):
        return self.found(self, user)

    def allowed_to_be_viewed_by(self, user):
        return self.project.allowed_to_be_viewed_by(user)

    allowed_to_be_deleted_by = allowed_to_be_created_by
        
    def __repr__(self):
        return '<Ticket[{}] title="{}">'.format(self.id, self.title)
