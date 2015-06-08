from alveare.resources import add_restful_endpoint
from flask.ext.login import login_required, current_user

def register_routes(api):

    from alveare.resources.user import UserCollection, UserResource
    api.add_resource(UserCollection, UserCollection.url)
    api.add_resource(UserResource, UserResource.url)

    from alveare.resources.auth import AuthCollection
    api.add_resource(AuthCollection, AuthCollection.url)

    from alveare.resources.auction import AuctionCollection, AuctionResource
    from alveare.resources.auction import AuctionBidEvents, AuctionEndEvents, AuctionFailEvents
    api.add_resource(AuctionCollection, '/auctions', endpoint='auctions')
    api.add_resource(AuctionResource, '/auctions/<int:id>', endpoint='auction')
    api.add_resource(AuctionBidEvents, '/auctions/<int:id>/bid_events', endpoint='auction_bid_events')
    api.add_resource(AuctionEndEvents, '/auctions/<int:id>/end_events', endpoint='auction_end_events')
    api.add_resource(AuctionFailEvents, '/auctions/<int:id>/fail_events', endpoint='auction_fail_events')

    from alveare.resources.work_events import WorkHaltEvents, WorkReviewEvents, WorkMediateEvents, WorkCompleteEvents, WorkResumeEvents, WorkFailEvents
    api.add_resource(WorkHaltEvents, '/work/<int:id>/halt_events')
    api.add_resource(WorkReviewEvents, '/work/<int:id>/review_events')
    api.add_resource(WorkMediateEvents, '/work/<int:id>/mediate_events')
    api.add_resource(WorkCompleteEvents, '/work/<int:id>/complete_events')
    api.add_resource(WorkResumeEvents, '/work/<int:id>/resume_events')
    api.add_resource(WorkFailEvents, '/work/<int:id>/fail_events')

    from alveare.models.internal_ticket import InternalTicket
    import alveare.views.internal_ticket as it_view
    add_restful_endpoint(api, InternalTicket, it_view.serializer, it_view.deserializer, it_view.update_deserializer)

    from alveare.models.github_ticket import GithubTicket
    import alveare.views.github_ticket as gt_view
    add_restful_endpoint(api, GithubTicket, gt_view.serializer, gt_view.deserializer, gt_view.update_deserializer)

    from alveare.models.ticket import Ticket
    import alveare.views.ticket as t_view
    add_restful_endpoint(api, Ticket, t_view.serializer, t_view.deserializer, t_view.update_deserializer)

    from alveare.models.bid_limit import BidLimit
    import alveare.views.bid_limit as bl_view
    add_restful_endpoint(api, BidLimit, bl_view.serializer, bl_view.deserializer, bl_view.update_deserializer)

    from alveare.models.ticket_set import TicketSet
    import alveare.views.ticket_set as ts_view
    add_restful_endpoint(api, TicketSet, ts_view.serializer, ts_view.deserializer, ts_view.update_deserializer)

    from alveare.models.job_fit import JobFit
    import alveare.views.job_fit as jf_view
    add_restful_endpoint(api, JobFit, jf_view.serializer, jf_view.deserializer, jf_view.update_deserializer)

    from alveare.models.organization import Organization
    import alveare.views.organization as o_view
    add_restful_endpoint(api, Organization, o_view.serializer, o_view.deserializer, o_view.update_deserializer)

    from alveare.models.manager import Manager
    import alveare.views.manager as m_view
    add_restful_endpoint(api, Manager, m_view.serializer, m_view.deserializer, m_view.update_deserializer)

    from alveare.models.work import Work
    import alveare.views.work as w_view
    add_restful_endpoint(api, Work, w_view.serializer, w_view.deserializer, w_view.update_deserializer)

    from alveare.models.review import Review
    import alveare.views.review as r_view
    add_restful_endpoint(api, Review, r_view.serializer, r_view.deserializer, r_view.update_deserializer)

    from alveare.models.project import Project
    import alveare.views.project as p_view
    add_restful_endpoint(api, Project, p_view.serializer, p_view.deserializer, p_view.update_deserializer)

    from alveare.models.github_project import GithubProject
    import alveare.views.github_project as gp_view
    add_restful_endpoint(api, GithubProject, gp_view.serializer, gp_view.deserializer, gp_view.update_deserializer)

    from alveare.models.code_repository import CodeRepository
    import alveare.views.code_repository as cr_view
    add_restful_endpoint(api, CodeRepository, cr_view.serializer, cr_view.deserializer, cr_view.update_deserializer)

    from alveare.models.mediation import Mediation
    import alveare.views.mediation as m_view
    add_restful_endpoint(api, Mediation, m_view.serializer, m_view.deserializer, m_view.update_deserializer)

    from alveare.models.arbitration import Arbitration
    import alveare.views.arbitration as a_view
    add_restful_endpoint(api, Arbitration, a_view.serializer, a_view.deserializer, a_view.update_deserializer)

    from alveare.models.debit import Debit
    import alveare.views.debit as d_view
    add_restful_endpoint(api, Debit, d_view.serializer, d_view.deserializer, d_view.update_deserializer)

    from alveare.models.credit import Credit
    import alveare.views.credit as c_view
    add_restful_endpoint(api, Credit, c_view.serializer, c_view.deserializer, c_view.update_deserializer)

    from alveare.models.bank_account import BankAccount
    import alveare.views.bank_account as ba_view
    add_restful_endpoint(api, BankAccount, ba_view.serializer, ba_view.deserializer, ba_view.update_deserializer)

    from alveare.models.work_offer import WorkOffer
    import alveare.views.work_offer as wo_view
    add_restful_endpoint(api, WorkOffer, wo_view.serializer, wo_view.deserializer, wo_view.update_deserializer)

    from alveare.models.ticket_snapshot import TicketSnapshot
    import alveare.views.ticket_snapshot as ts_view
    add_restful_endpoint(api, TicketSnapshot, ts_view.serializer, ts_view.deserializer, ts_view.update_deserializer)

    from alveare.models.bid import Bid
    import alveare.views.bid as bid_view
    add_restful_endpoint(api, Bid, bid_view.serializer, bid_view.deserializer, bid_view.update_deserializer)

    from alveare.models.ticket_match import TicketMatch
    import alveare.views.ticket_match as tm_view
    add_restful_endpoint(api, TicketMatch, tm_view.serializer, tm_view.deserializer, tm_view.update_deserializer)

    from alveare.models.nomination import Nomination
    import alveare.views.nomination as n_view
    add_restful_endpoint(api, Nomination, n_view.serializer, n_view.deserializer, n_view.update_deserializer)

    from alveare.models.github_account import GithubAccount
    import alveare.views.github_account as ga_view
    add_restful_endpoint(api, GithubAccount, ga_view.serializer, ga_view.deserializer, ga_view.update_deserializer, None)

    from alveare.models.remote_work_history import RemoteWorkHistory
    import alveare.views.remote_work_history as rwh_view
    add_restful_endpoint(api, RemoteWorkHistory, rwh_view.serializer, rwh_view.deserializer, rwh_view.update_deserializer, None)

    from alveare.models.skill_requirement import SkillRequirement
    import alveare.views.skill_requirement as sr_view
    add_restful_endpoint(api, SkillRequirement, sr_view.serializer, sr_view.deserializer, sr_view.update_deserializer, None)

    from alveare.models.remote_ticket import RemoteTicket
    import alveare.views.remote_ticket as rt_view
    add_restful_endpoint(api, RemoteTicket, rt_view.serializer, rt_view.deserializer, rt_view.update_deserializer, None)

    from alveare.models.code_clearance import CodeClearance
    import alveare.views.code_clearance as cc_view
    add_restful_endpoint(api, CodeClearance, cc_view.serializer, cc_view.deserializer, cc_view.update_deserializer, None)

    from alveare.models.skill_set import SkillSet
    import alveare.views.skill_set as ss_view
    add_restful_endpoint(api, SkillSet, ss_view.serializer, ss_view.deserializer, ss_view.update_deserializer, None)

    from alveare.models.contractor import Contractor
    import alveare.views.contractor as c_view
    add_restful_endpoint(api, Contractor, c_view.serializer, c_view.deserializer, c_view.update_deserializer, None)

    from alveare.models.term_sheet import TermSheet
    import alveare.views.term_sheet as ts_view
    add_restful_endpoint(api, TermSheet, ts_view.serializer, ts_view.deserializer, ts_view.update_deserializer, None)

    from alveare.models.contract import Contract
    import alveare.views.contract as c_view
    add_restful_endpoint(api, Contract, c_view.serializer, c_view.deserializer, c_view.update_deserializer, None)

    from alveare.models.feedback import Feedback
    import alveare.views.feedback as f_view
    add_restful_endpoint(api, Feedback, f_view.serializer, f_view.deserializer, f_view.update_deserializer, None)

    from alveare.models.comment import Comment
    import alveare.views.comment as c_view
    add_restful_endpoint(api, Comment, c_view.serializer, c_view.deserializer, c_view.update_deserializer, None)
