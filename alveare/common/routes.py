from alveare.resources import add_alveare_resource

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

    from alveare.resources.project import ProjectCollection, ProjectResource
    api.add_resource(ProjectCollection, '/projects', endpoint='projects')
    api.add_resource(ProjectResource, '/projects/<int:id>', endpoint='project')

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

    from alveare.resources.work_offer import WorkOfferCollection, WorkOfferResource
    api.add_resource(WorkOfferCollection, '/work_offers', endpoint='work_offers')
    api.add_resource(WorkOfferResource, '/work_offers/<int:id>', endpoint='work_offer')

    from alveare.resources.ticket_snapshot import TicketSnapshotCollection, TicketSnapshotResource
    api.add_resource(TicketSnapshotCollection, '/ticket_snapshots', endpoint='ticket_snapshots')
    api.add_resource(TicketSnapshotResource, '/ticket_snapshots/<int:id>', endpoint='ticket_snapshot')

    from alveare.resources.contractor import ContractorCollection, ContractorResource
    api.add_resource(ContractorCollection, '/contractors', endpoint='contractors')
    api.add_resource(ContractorResource, '/contractors/<int:id>', endpoint='contractor')

    from alveare.resources.bid import BidCollection, BidResource
    api.add_resource(BidCollection, '/bids', endpoint='bids')
    api.add_resource(BidResource, '/bids/<int:id>', endpoint='bid')

    from alveare.resources.auction import AuctionCollection, AuctionResource
    api.add_resource(AuctionCollection, '/auctions', endpoint='auctions')
    api.add_resource(AuctionResource, '/auctions/<int:id>', endpoint='auction')

    from alveare.models.github_account import GithubAccount
    import alveare.views.github_account as github_account_view
    add_alveare_resource(
        api,
        GithubAccount,
        'github_account',
        'github_accounts',
        '/<int:id>',
        github_account_view.serializer,
        github_account_view.deserializer,
        github_account_view.update_deserializer
    )

    from alveare.models.remote_work_history import RemoteWorkHistory
    import alveare.views.remote_work_history as remote_work_history_view
    add_alveare_resource(
        api,
        RemoteWorkHistory,
        'remote_work_history',
        'remote_work_histories',
        '/<int:id>',
        remote_work_history_view.serializer,
        remote_work_history_view.deserializer,
        remote_work_history_view.update_deserializer
    )

    from alveare.models.ticket import Ticket
    import alveare.views.ticket as ticket_view
    add_alveare_resource(
        api,
        Ticket,
        'ticket',
        'tickets',
        '/<int:id>',
        ticket_view.serializer,
        ticket_view.deserializer,
        ticket_view.update_deserializer
    )

    from alveare.models.internal_ticket import InternalTicket
    import alveare.views.internal_ticket as internal_ticket_view
    add_alveare_resource(
        api,
        InternalTicket,
        'internal_ticket',
        'internal_tickets',
        '/<int:id>',
        internal_ticket_view.serializer,
        internal_ticket_view.deserializer,
        internal_ticket_view.update_deserializer
    )

    from alveare.models.github_ticket import GithubTicket
    import alveare.views.github_ticket as github_ticket_view
    add_alveare_resource(
        api,
        GithubTicket,
        'github_ticket',
        'github_tickets',
        '/<int:id>',
        github_ticket_view.serializer,
        github_ticket_view.deserializer,
        github_ticket_view.update_deserializer
    )

    from alveare.models.remote_ticket import RemoteTicket
    import alveare.views.remote_ticket as remote_ticket_view
    add_alveare_resource(
        api,
        RemoteTicket,
        'remote_ticket',
        'remote_tickets',
        '/<int:id>',
        remote_ticket_view.serializer,
        remote_ticket_view.deserializer,
        remote_ticket_view.update_deserializer
    )
