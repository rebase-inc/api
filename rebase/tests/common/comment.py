from random import randrange
from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name, pick_a_word

def base_scenario(db, make_ticket_comment=False, make_mediation_comment=False, make_review_comment=False, make_feedback_comment=False):
    mgr_user =      mock.create_one_user(db)
    org =           mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project =       mock.create_one_github_project(db, org, pick_a_word().capitalize()+' Project')
    ticket =        mock.create_one_github_ticket(db, randrange(10*3, 10*4), project)
    contractor =    mock.create_one_contractor(db)
    clearance =     mock.create_one_code_clearance(db, project, contractor)

    if make_review_comment or make_mediation_comment or make_feedback_comment:
        auction =       mock.create_one_auction(db, [ticket])
        nomination =    mock.create_one_nomination(db, auction, contractor, approved=True)
        snapshot =      ticket.snapshots[0]
        work_offer =    mock.create_work_offer(db, contractor, snapshot, randrange(10*2, 10*3))
        work =          models.Work(work_offer)
        mediation =     models.Mediation(work)
        review =        models.Review(work)
        review.rating = randrange(1,5)

    comment_text = "I say: " + pick_a_word() + " to you sir!"

    if make_ticket_comment:
        comment = models.Comment(mgr_user, comment_text, ticket=ticket)
    if make_mediation_comment:
        comment = models.Comment(mgr_user, comment_text, mediation=mediation)
    if make_review_comment:
        comment = models.Comment(mgr_user, comment_text, review=review)
    if make_feedback_comment:
        feedback =      mock.create_one_feedback(db, auction, contractor)
        comment = feedback.comment

    db.session.commit()
    return mgr_user, contractor.user, comment

def case_mgr_ticket_comment(db):
    mgr_user, _, comment = base_scenario(db, make_ticket_comment = True)
    return mgr_user, comment

def case_contractor_ticket_comment(db):
    _, contractor_user, comment = base_scenario(db, make_ticket_comment = True)
    return contractor_user, comment

def case_mgr_mediation_comment(db):
    mgr_user, _, comment = base_scenario(db, make_mediation_comment=True)
    return mgr_user, comment

def case_contractor_mediation_comment(db):
    _, contractor_user, comment = base_scenario(db, make_mediation_comment=True)
    return contractor_user, comment

def case_mgr_review_comment(db):
    mgr_user, _, comment = base_scenario(db, make_review_comment=True)
    return mgr_user, comment

def case_contractor_review_comment(db):
    _, contractor_user, comment = base_scenario(db, make_review_comment=True)
    return contractor_user, comment

def case_mgr_feedback_comment(db):
    mgr_user, _, comment = base_scenario(db, make_feedback_comment=True)
    return mgr_user, comment

def case_contractor_feedback_comment(db):
    _, contractor_user, comment = base_scenario(db, make_feedback_comment=True)
    return contractor_user, comment
