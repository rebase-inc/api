
from rebase import models
from rebase.common import mock
from rebase.tests.common.use_case import UseCase

class OrganizationUseCase(UseCase):

    def base_scenario(self, db):
        project_1 = mock.create_one_github_project(db)
        org_1 = project_1.organization
        user_1 = project_1.managers[0].user

        project_2 = mock.create_one_github_project(db)
        org_2 = project_2.organization
        user_2 = project_2.managers[0].user

        contractor_1 = mock.create_contractor(db, user=user_1)
        contractor_2 = mock.create_contractor(db, user=user_2)

        cc_1 = mock.create_one_code_clearance(db, project=project_2, contractor=contractor_1)
        cc_2 = mock.create_one_code_clearance(db, project=project_1, contractor=contractor_2)

        db.session.commit()
        return user_1, user_2, org_1, org_2
