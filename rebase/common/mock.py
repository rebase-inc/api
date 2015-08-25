import datetime
import uuid
from random import randint
from .utils import (
    pick_a_word,
    pick_a_first_name,
    pick_a_last_name,
    pick_an_organization_name,
)

FAKE_COMMENTS = [
    '@rapha, I\'m convinced that you were right regarding the composite primary keys being a better choice. However, in the few places where we are using composite primary keys right now, I don’t think the relationship is being properly referenced. See the SQLAlchemy documentation for proper reference of a composite foreign key.',
    'What do you mean? Is this not correct (from job_fit model)? ```__table_args__ = ( DB.ForeignKeyConstraint( [contractor_id, ticket_set_id], [Nomination.contractor_id, Nomination.ticket_set_id], ondelete=\'CASCADE\'), {})```',
    'Hmm, that does look correct. The one I was looking at is in the bid model. It indirectly references the auction and contractor ids through the nomination model, though it doesn’t specifically reference the nomination model. This should instead be switched to a reference like above. I guess I should\'ve actually looked into the places where this was happening.',
]

def create_one_organization(db, name=None, user=None):
    from rebase.models import Organization
    user = user or create_one_user(db)
    organization = Organization(name or pick_an_organization_name(), user)
    db.session.add(organization)
    return organization

def create_one_user(db, first_name=None, last_name=None, email=None, password='foo', admin=False):
    from rebase.models import User
    email = email or 'user-{}@rebase.io'.format(uuid.uuid4())
    user = User(
        first_name or pick_a_first_name(),
        last_name or pick_a_last_name(),
        email,
        password
    )
    user.admin = admin
    db.session.add(user)
    return user

def create_one_manager(db, user=None, org=None):
    from rebase.models import Manager
    user = user or create_one_user(db)
    organization = org or create_one_organization(db)
    manager = Manager(user, organization)
    db.session.add(manager)
    return manager

def create_one_contractor(db, user=None):
    from rebase.models import Contractor, SkillSet
    user = user or create_one_user(db)
    contractor = Contractor(user)
    SkillSet(contractor)
    db.session.add(contractor)
    return contractor

def create_one_bank_account(db, owner):
    from rebase.models import BankAccount, Organization, Contractor
    routing = 123456000+randint(0, 999)
    account = 1230000+randint(0, 9999)
    if isinstance(owner, Organization):
        account = BankAccount('Main Account', routing, account, organization=owner)
    elif isinstance(owner, Contractor):
        account = BankAccount('Main Account', routing, account, contractor=owner)
    else:
        raise ValueError('owner is of type "{}", should be Organization or Contractor'.format(type(owner)))
    db.session.add(account)
    return account

def create_one_code_clearance(db, project=None, contractor=None, pre_approved=False):
    from rebase.models import CodeClearance
    contractor = contractor or create_one_contractor(db)
    project = project or create_one_project(db)
    code_clearance = CodeClearance(project, contractor, pre_approved)
    db.session.add(code_clearance)
    return code_clearance

def create_one_remote_work_history(db, contractor=None):
    from rebase.models import RemoteWorkHistory
    contractor = contractor or create_one_contractor(db)
    remote_work_history = RemoteWorkHistory(contractor)
    db.session.add(remote_work_history)
    return remote_work_history

def create_one_github_account(db, remote_work_history=None, user_name='ravioli'):
    from rebase.models import GithubAccount
    remote_work_history = remote_work_history or create_one_remote_work_history(db)
    github_account = GithubAccount(remote_work_history, user_name)
    db.session.add(github_account)
    return github_account

def create_one_project(db, organization=None, project_name=None):
    from rebase.models import Organization, Project, CodeRepository
    organization = organization or create_one_organization(db)
    project = Project(organization, project_name or pick_a_word().capitalize()+' Project')
    code_repo = CodeRepository(project)
    db.session.add(organization)
    db.session.add(project)
    db.session.add(code_repo)
    return project

def create_one_remote_project(db, organization_name='Rebase', project_name='api'):
    from rebase.models import Organization, RemoteProject, CodeRepository
    organization = create_one_organization(db, organization_name)
    remote_project = RemoteProject(organization, project_name)
    code_repo = CodeRepository(remote_project)
    db.session.add(organization)
    db.session.add(remote_project)
    db.session.add(code_repo)
    return remote_project

def create_one_github_project(db, organization=None, project_name='api'):
    from rebase.models import Organization, GithubProject, CodeRepository
    organization = organization or create_one_organization(db, 'Rebase')
    github_project = GithubProject(organization, project_name)
    code_repo = CodeRepository(github_project)
    db.session.add(github_project)
    return github_project

def create_one_internal_ticket(db, title, description=None, project=None):
    from rebase.models import InternalTicket, SkillRequirement, Comment
    project = project or create_one_project(db)
    description = description or ' '.join(pick_a_word() for i in range(5))
    ticket = InternalTicket(project, title, description)
    SkillRequirement(ticket)
    db.session.add(ticket)
    return ticket

def create_one_remote_ticket(db, title, description=None, project=None):
    from rebase.models import RemoteTicket, SkillRequirement
    project = project or create_one_project(db)
    description = description or title + '-DESCRIPTION'
    ticket = RemoteTicket(project, title, description)
    SkillRequirement(ticket)
    db.session.add(ticket)
    return ticket

def create_one_github_ticket(db, number, project=None):
    from rebase.models import GithubTicket, SkillRequirement
    project = project or create_one_github_project(db)
    ticket = GithubTicket(project, number)
    SkillRequirement(ticket)

    db.session.add(ticket)
    return ticket

def create_some_tickets(db, ticket_titles=None):
    from rebase.models import InternalTicket, RemoteTicket, SkillRequirement
    project = create_one_project(db)
    ticket_titles = ticket_titles or ['Foo', 'Bar', 'Baz', 'Qux']
    tickets = []
    for title in ticket_titles:
        ticket = InternalTicket(project, title)
        SkillRequirement(ticket)
        tickets.append(ticket)
    db.session.add_all(tickets)
    return tickets

def create_ticket_matches(db, tickets=None, contractor=None):
    from rebase.models import TicketMatch
    tickets = tickets or create_some_tickets(db)
    contractor = contractor or create_one_contractor(db)
    ticket_matches = []
    for ticket in tickets:
        ticket_matches.append(TicketMatch(contractor.skill_set, ticket.skill_requirement, 100))
    db.session.add_all(ticket_matches)
    return ticket_matches

def create_one_snapshot(db, ticket=None):
    from rebase.models import InternalTicket, TicketSnapshot, SkillRequirement
    if not ticket:
        ticket = InternalTicket(create_one_project(db), 'for a snapshot')
        SkillRequirement(ticket)
        db.session.add(ticket)
    ts = TicketSnapshot(ticket or InternalTicket(create_one_project(db), 'for a snapshot'))
    db.session.add(ts)
    return ts

def create_one_auction(db, tickets=None, duration=1000, finish_work_by=None, redundancy=1):
    finish_work_by = finish_work_by or datetime.datetime.now() + datetime.timedelta(days=2)
    from rebase.models import Auction, TicketSet, BidLimit, TicketSnapshot, TermSheet
    tickets = tickets or create_some_tickets(db)
    ticket_snaps = [TicketSnapshot(ticket) for ticket in tickets]
    bid_limits = [BidLimit(ticket_snap, 200) for ticket_snap in ticket_snaps]
    term_sheet = TermSheet('Some legal mumbo-jumbo')
    ticket_set = TicketSet(bid_limits)
    organization = tickets[0].project.organization
    auction = Auction(ticket_set, term_sheet, duration, finish_work_by, redundancy)
    db.session.add(auction)
    return auction

def create_one_nomination(db, auction=None, contractor=None, approved=False):
    from rebase.models import Nomination
    auction = auction or create_one_auction(db)
    contractor = contractor or create_one_contractor(db)
    nomination = Nomination(contractor, auction.ticket_set)
    if approved:
        auction.approved_talents.append(nomination)
    db.session.add(nomination)
    return nomination

def create_one_job_fit(db, nomination=None, ticket_matches=None):
    from rebase.models import TicketMatch, JobFit
    nomination = nomination or create_one_nomination(db)
    skill_set = nomination.contractor.skill_set
    if not ticket_matches:
        ticket_matches = []
        for bid_limit in nomination.ticket_set.bid_limits:
            ticket_matches.append(TicketMatch(skill_set, bid_limit.ticket_snapshot.ticket.skill_requirement, 100))
    job_fit = JobFit(nomination, ticket_matches)
    db.session.add(job_fit)
    return job_fit

def create_one_feedback(db, auction=None, contractor=None, comment=None):
    from rebase.models import Feedback, Comment

    feedback = Feedback(
        auction or create_one_auction(db),
        contractor or create_one_contractor(db)
    )
    Comment(comment or 'Your auction sucks', feedback=feedback)
    db.session.add(feedback)
    return feedback

def create_work_offer(db, contractor, snapshot, price):
    from rebase.models import WorkOffer
    offer = WorkOffer(contractor, snapshot, price)
    db.session.add(offer)
    return offer

def create_one_bid(db):
    from rebase.models import Bid, WorkOffer
    auction = create_one_auction(db)
    contractor = create_one_contractor(db)
    work_offers = []
    for bid_limit in auction.ticket_set.bid_limits:
        work_offers.append(WorkOffer(contractor, bid_limit.ticket_snapshot, 150))
    bid = Bid(auction, contractor)
    db.session.add(bid)
    return bid

def create_one_contract(db):
    from rebase.models import Contract
    bid = create_one_bid(db)
    contract = Contract(bid)
    db.session.add(bid)
    return contract

def create_some_work(db, review=True, debit_credit=True, mediation=True, arbitration=True):
    from rebase.models import Work, Review, Debit, Credit, Mediation, Arbitration
    bid = create_one_bid(db)
    works = []
    for work_offer in bid.work_offers:
        work = Work(work_offer)
        works.append(work)
        if review:
            _ = Review(work, 5)
        if debit_credit:
            _ = Debit(work, 100)
            _ = Credit(work, 120)
        if mediation:
            m = Mediation(work)
            if arbitration:
                _ = Arbitration(m)
        db.session.add(work)
    return works

def create_one_work_review(db, rating, comment):
    from rebase.models import Review, Comment
    work = create_some_work(db, review=False).pop()
    review = Review(work, rating)
    comment = Comment(comment, review=review)
    db.session.add(review)
    return review

def create_admin_user(db, password):
    god = create_one_user(db, 'Flying', 'SpaghettiMonster', 'fsm@rebase.io', password)
    god.admin = True
    return god


class UserStory(object):
    types = { 'NEW_DEVELOPER' : 'NEW_DEVELOPER' }

    def __init__(self, type, first_name, last_name, email, password):
        if type == self.types['NEW_DEVELOPER']:
            pass
        else:
            raise Exception('Invalid type!')
        self.type = type
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def create(self, db):
        if self.type == self.types['NEW_DEVELOPER']:
            self.user = create_one_user(db, self.first_name, self.last_name, self.email, self.password)
            user_ted = create_one_user(db, 'Ted', 'Crisp', 'tedcrisp@joinrebase.com')
            org_veridian = create_one_organization(db, 'veridian', user_ted)
            manager_ted = create_one_manager(db, user_ted, org_veridian)
            project_matchmaker = create_one_project(db, manager_ted.organization, 'matchmaker')
            the_tickets = [create_one_internal_ticket(db, 'Issue #{}'.format(i), project=project_matchmaker) for i in range(10)]
            self.contractor = create_one_contractor(db, self.user)
            the_matches = create_ticket_matches(db, the_tickets, self.contractor)
            the_auctions = [create_one_auction(db, [ticket]) for ticket in the_tickets]
            the_nominations = [create_one_nomination(db, auction, self.contractor) for auction in the_auctions]
            the_job_fits = [create_one_job_fit(db, nomination, match) for nomination, match in zip(the_nominations, the_matches)]


def create_the_world(db):
    dev_user_story = UserStory('NEW_DEVELOPER', 'Phil', 'Meyman', 'philmeyman@joinrebase.com', 'lem')
    dev_user_story.create(db)
    andrew = create_one_user(db, 'Andrew', 'Millspaugh', 'andrew@manager.rebase.io')
    rapha = create_one_user(db, 'Raphael', 'Goyran', 'raphael@rebase.io')
    joe = create_one_user(db, 'Joe', 'Pesci', 'joe@rebase.io')
    tim = create_one_user(db, 'Tim', 'Pesci', 'tim@rebase.io')
    create_one_snapshot(db)
    create_one_snapshot(db)
    steve = create_one_user(db, 'Steve', 'Gildred', 'steve@rebase.io')
    manager_andrew = create_one_manager(db, andrew) # also creates an organization
    manager_rapha = create_one_manager(db, rapha)
    bigdough_project = create_one_github_project(db, manager_rapha.organization, 'Big Dough')

    internal_project = create_one_project(db, manager_rapha.organization)
    internal_project_tickets = [create_one_internal_ticket(db, 'Issue #{}'.format(i), project=internal_project) for i in range(10)]

    manhattan_project = create_one_github_project(db, manager_andrew.organization, 'Manhattan')
    manhattan_tickets = [ create_one_github_ticket(db, ticket_number, manhattan_project) for ticket_number in range(10) ]
    rapha_contractor = create_one_contractor(db, rapha)
    steve_contractor = create_one_contractor(db, steve)
    tim_contractor = create_one_contractor(db, tim)
    manhattan_ticket_matches = create_ticket_matches(db, manhattan_tickets, rapha_contractor)
    manhattan_auction = create_one_auction(db, manhattan_tickets)
    rapha_nomination = create_one_nomination(db, manhattan_auction, rapha_contractor)
    steve_nomination = create_one_nomination(db, manhattan_auction, steve_contractor)
    rapha_manhattan_job_fit = create_one_job_fit(db, rapha_nomination, manhattan_ticket_matches)
    create_one_code_clearance(db, manhattan_project, rapha_contractor, pre_approved=True)
    create_one_code_clearance(db, manhattan_project, steve_contractor, pre_approved=False)
    create_one_code_clearance(db, bigdough_project, steve_contractor, pre_approved=True)
    create_one_code_clearance(db, internal_project, steve_contractor, pre_approved=True)
    create_one_bank_account(db, rapha_contractor)
    rapha_rwh = create_one_remote_work_history(db, rapha_contractor)
    create_one_github_account(db, rapha_rwh, 'rapha.opensource')
    create_one_github_account(db, rapha_rwh, 'rapha-la-mitraille')
    create_one_feedback(db)
    create_one_feedback(db)
    create_one_contract(db)
    create_one_contract(db)
    create_some_work(db)
    create_some_work(db, review=False)
    create_some_work(db, mediation=False)
    create_some_work(db, arbitration=False)
    create_some_work(db, debit_credit=False)
    create_one_work_review(db, 5, 'It was amazing')
    create_one_work_review(db, 3, 'Meh')
