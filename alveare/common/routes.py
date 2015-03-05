
def register_routes(api):
    from alveare.resources.user import UserCollection, UserResource
    api.add_resource(UserCollection, '/users', endpoint='users')
    api.add_resource(UserResource, '/users/<int:id>', endpoint='user')

    from alveare.resources.organization import OrganizationCollection, OrganizationResource
    api.add_resource(OrganizationCollection, '/organizations', endpoint='organizations')
    api.add_resource(OrganizationResource, '/organizations/<int:id>', endpoint='organization')

    from alveare.resources.manager import ManagerCollection, ManagerResource
    api.add_resource(ManagerCollection, '/managers', endpoint='managers')
    api.add_resource(ManagerResource, '/managers/<int:id>', endpoint='manager')

    from alveare.resources.work import WorkCollection, WorkResource
    api.add_resource(WorkCollection, '/work', endpoint='works')
    api.add_resource(WorkResource, '/work/<int:id>', endpoint='work')

    from alveare.resources.review import ReviewCollection, ReviewResource
    api.add_resource(ReviewCollection, '/reviews', endpoint='reviews')
    api.add_resource(ReviewResource, '/reviews/<int:id>', endpoint='review')

    from alveare.resources.github_project import GithubProjectCollection, GithubProjectResource
    api.add_resource(GithubProjectCollection, '/github_projects', endpoint='github_projects')
    api.add_resource(GithubProjectResource, '/github_projects/<int:id>', endpoint='github_project')

    from alveare.resources.code_repository import CodeRepositoryCollection, CodeRepositoryResource
    api.add_resource(CodeRepositoryCollection, '/code_repositories', endpoint='code_repositories')
    api.add_resource(CodeRepositoryResource, '/code_repositories/<int:id>', endpoint='code_repository')

    from alveare.resources.mediation import MediationCollection, MediationResource
    api.add_resource(MediationCollection, '/mediations', endpoint='mediations')
    api.add_resource(MediationResource, '/mediations/<int:id>', endpoint='mediation')

    from alveare.resources.arbitration import ArbitrationCollection, ArbitrationResource
    api.add_resource(ArbitrationCollection, '/arbitrations', endpoint='arbitrations')
    api.add_resource(ArbitrationResource, '/arbitrations/<int:id>', endpoint='arbitration')

    from alveare.resources.debit import DebitCollection, DebitResource
    api.add_resource(DebitCollection, '/debits', endpoint='debits')
    api.add_resource(DebitResource, '/debits/<int:id>', endpoint='debit')

    from alveare.resources.credit import CreditCollection, CreditResource
    api.add_resource(CreditCollection, '/credits', endpoint='credits')
    api.add_resource(CreditResource, '/credits/<int:id>', endpoint='credit')

    from alveare.resources.bank_account import BankAccountCollection, BankAccountResource
    api.add_resource(BankAccountCollection, '/bank_accounts', endpoint='bank_accounts')
    api.add_resource(BankAccountResource, '/bank_accounts/<int:id>', endpoint='bank_account')
