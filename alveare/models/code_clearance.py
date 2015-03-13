
from alveare.common.database import DB

from .project import Project
from .contractor import Contractor

class CodeClearance(DB.Model):
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
        return '<CodeClearance[id:{}] for {}, pre_approved={}>'.format(self.id, self.project, self.pre_approved)

