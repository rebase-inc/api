from rebase.resources import add_restful_endpoint, RestfulResource
from rebase.common.keys import make_resource_url

def register_routes(api):

    from rebase.resources.user import UserCollection, UserResource
    api.add_resource(UserCollection, UserCollection.url)
    api.add_resource(UserResource, UserResource.url)

    from rebase.models.role import Role
    import rebase.views.role as role_view
    add_restful_endpoint(api, Role, role_view.serializer, role_view.deserializer, role_view.update_deserializer)

    from rebase.resources.auth import AuthCollection
    api.add_resource(AuthCollection, AuthCollection.url)

    from rebase.resources.c2r_auth import C2RAuthCollection
    api.add_resource(C2RAuthCollection, C2RAuthCollection.url)

    from rebase.resources.auction import add_auction_resource
    add_auction_resource(api)

    from rebase.resources.github_account import GithubAccountCollection
    api.add_resource(GithubAccountCollection, '/github_accounts', endpoint='github_accounts')
    import rebase.views.github_account as gh_account_views
    from rebase.models import GithubAccount
    github_account_resource = RestfulResource(GithubAccount, gh_account_views.serializer, gh_account_views.deserializer, gh_account_views.update_deserializer)
    api.add_resource(github_account_resource, make_resource_url(GithubAccount), endpoint = GithubAccount.__pluralname__ + '_resource')

    from rebase.resources.mediation import add_mediation_resource
    add_mediation_resource(api)

    from rebase.models.internal_ticket import InternalTicket
    import rebase.views.internal_ticket as it_view
    add_restful_endpoint(api, InternalTicket, it_view.serializer, it_view.deserializer, it_view.update_deserializer)

    from rebase.resources.ticket import add_ticket_resource
    add_ticket_resource(api)

    from rebase.models.github_ticket import GithubTicket
    import rebase.views.github_ticket as gt_view
    add_restful_endpoint(api, GithubTicket, gt_view.serializer, gt_view.deserializer, gt_view.update_deserializer)

    from rebase.models.bid_limit import BidLimit
    import rebase.views.bid_limit as bl_view
    add_restful_endpoint(api, BidLimit, bl_view.serializer, bl_view.deserializer, bl_view.update_deserializer)

    from rebase.models.ticket_set import TicketSet
    import rebase.views.ticket_set as ts_view
    add_restful_endpoint(api, TicketSet, ts_view.serializer, ts_view.deserializer, ts_view.update_deserializer)

    from rebase.models.job_fit import JobFit
    import rebase.views.job_fit as jf_view
    add_restful_endpoint(api, JobFit, jf_view.serializer, jf_view.deserializer, jf_view.update_deserializer)

    from rebase.models.organization import Organization
    import rebase.views.organization as o_view
    add_restful_endpoint(api, Organization, o_view.serializer, o_view.deserializer, o_view.update_deserializer)

    from rebase.resources.manager import add_manager_resource
    add_manager_resource(api)

    from rebase.resources.work import add_work_resource
    add_work_resource(api)

    from rebase.resources.review import add_review_resource
    add_review_resource(api)

    from rebase.resources.project import add_project_resource
    add_project_resource(api)

    from rebase.resources.ssh_key import add_ssh_key_resource
    add_ssh_key_resource(api)

    from rebase.resources.nomination import add_nomination_resource
    add_nomination_resource(api)

    from rebase.resources.code_clearance import add_code_clearance_resource
    add_code_clearance_resource(api)

    from rebase.models.github_project import GithubProject
    import rebase.views.github_project as gp_view
    add_restful_endpoint(api, GithubProject, gp_view.serializer, gp_view.deserializer, gp_view.update_deserializer)

    from rebase.models.internal_project import InternalProject
    import rebase.views.internal_project as gp_view
    add_restful_endpoint(api, InternalProject, gp_view.serializer, gp_view.deserializer, gp_view.update_deserializer)

    from rebase.models.code_repository import CodeRepository
    import rebase.views.code_repository as cr_view
    add_restful_endpoint(api, CodeRepository, cr_view.serializer, cr_view.deserializer, cr_view.update_deserializer)

    from rebase.models.arbitration import Arbitration
    import rebase.views.arbitration as a_view
    add_restful_endpoint(api, Arbitration, a_view.serializer, a_view.deserializer, a_view.update_deserializer)

    from rebase.models.debit import Debit
    import rebase.views.debit as d_view
    add_restful_endpoint(api, Debit, d_view.serializer, d_view.deserializer, d_view.update_deserializer)

    from rebase.models.credit import Credit
    import rebase.views.credit as c_view
    add_restful_endpoint(api, Credit, c_view.serializer, c_view.deserializer, c_view.update_deserializer)

    from rebase.models.bank_account import BankAccount
    import rebase.views.bank_account as ba_view
    add_restful_endpoint(api, BankAccount, ba_view.serializer, ba_view.deserializer, ba_view.update_deserializer)

    from rebase.models.work_offer import WorkOffer
    import rebase.views.work_offer as wo_view
    add_restful_endpoint(api, WorkOffer, wo_view.serializer, wo_view.deserializer, wo_view.update_deserializer)

    from rebase.models.ticket_snapshot import TicketSnapshot
    import rebase.views.ticket_snapshot as ts_view
    add_restful_endpoint(api, TicketSnapshot, ts_view.serializer, ts_view.deserializer, ts_view.update_deserializer)

    from rebase.models.bid import Bid
    import rebase.views.bid as bid_view
    add_restful_endpoint(api, Bid, bid_view.serializer, bid_view.deserializer, bid_view.update_deserializer)

    from rebase.models.ticket_match import TicketMatch
    import rebase.views.ticket_match as tm_view
    add_restful_endpoint(api, TicketMatch, tm_view.serializer, tm_view.deserializer, tm_view.update_deserializer)

    from rebase.models.remote_work_history import RemoteWorkHistory
    import rebase.views.remote_work_history as rwh_view
    add_restful_endpoint(api, RemoteWorkHistory, rwh_view.serializer, rwh_view.deserializer, rwh_view.update_deserializer)

    from rebase.models.skill_requirement import SkillRequirement
    import rebase.views.skill_requirement as sr_view
    add_restful_endpoint(api, SkillRequirement, sr_view.serializer, sr_view.deserializer, sr_view.update_deserializer)

    from rebase.models.remote_ticket import RemoteTicket
    import rebase.views.remote_ticket as rt_view
    add_restful_endpoint(api, RemoteTicket, rt_view.serializer, rt_view.deserializer, rt_view.update_deserializer)

    from rebase.models.skill_set import SkillSet
    import rebase.views.skill_set as ss_view
    add_restful_endpoint(api, SkillSet, ss_view.serializer, ss_view.deserializer, ss_view.update_deserializer)

    from rebase.models.contractor import Contractor
    import rebase.views.contractor as c_view
    add_restful_endpoint(api, Contractor, c_view.serializer, c_view.deserializer, c_view.update_deserializer)

    from rebase.models.term_sheet import TermSheet
    import rebase.views.term_sheet as ts_view
    add_restful_endpoint(api, TermSheet, ts_view.serializer, ts_view.deserializer, ts_view.update_deserializer)

    from rebase.resources.contract import add_contract_resource
    add_contract_resource(api)

    from rebase.models.feedback import Feedback
    import rebase.views.feedback as f_view
    add_restful_endpoint(api, Feedback, f_view.serializer, f_view.deserializer, f_view.update_deserializer)

    from rebase.resources.comment import add_comment_resource
    add_comment_resource(api)
