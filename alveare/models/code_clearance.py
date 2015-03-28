
from sqlalchemy import and_, or_

from functools import reduce, partial

from alveare.common.database import DB

from .project import Project
from .contractor import Contractor
from .role import Role
from .manager import Manager
from .organization import Organization

class CodeClearance(DB.Model):
    __pluralname__ = 'code_clearances'

    id =            DB.Column(DB.Integer, primary_key=True)
    pre_approved =  DB.Column(DB.Boolean, nullable=False)
    project_id =    DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), nullable=False)


    def __init__(self, project, contractor, pre_approved=False):
        if not isinstance(project, Project):
            raise ValueError('{} field on {} must be {} not {}'.format('project', self.__tablename__, Project, type(project)))
        if not isinstance(contractor, Contractor):
            raise ValueError('{} field on {} must be {} not {}'.format('contractor', self.__tablename__, Contractor, type(contractor)))
        self.project = project
        self.contractor = contractor
        self.pre_approved = pre_approved

    def __repr__(self):
        return '<CodeClearance[id:{} project:"{}" contractor:"{}" pre_approved:{}>'.format(
            self.id,
            self.project.name,
            self.contractor.user.first_name+' '+self.contractor.user.last_name,
            self.pre_approved
        )

    def in_managers(self, user_id):
        return CodeClearance.query\
            .join(Project, Project.id == self.project_id)\
            .join(Organization)\
            .join(Manager, Manager.user_id == user_id)\

    def is_contractor(self, user_id):
        return CodeClearance.query.join(Contractor, Contractor.user_id == user_id)

    def allows_get(self, user):
        return self.is_contractor(user.id).union(self.in_managers(user.id)).limit(100).all()

    def allows_modify(self, user):
        return self.in_managers(user.id).limit(100).all()

    def all_clearances_as_contractor(current_user):
        return CodeClearance.query\
            .join(Contractor)\
            .filter(Contractor.user == current_user)


    def all_clearances_as_manager(current_user):
        return CodeClearance.query\
            .join(Project)\
            .join(Organization)\
            .join(Manager)\
            .filter(Manager.user == current_user)

    def get_all(current_user):
        if current_user.is_admin():
            return CodeClearance.query
        return\
            CodeClearance.all_clearances_as_manager(current_user)\
            .union(\
            CodeClearance.all_clearances_as_contractor(current_user))
