import datetime
from random import randint

def create_one_organization(db, name='Alveare'):
    from alveare.models import Organization
    user = create_one_user(db)
    organization = Organization(name, user)
    db.session.add(organization)
    return organization

def create_one_user(db, first_name='Andrew', last_name='Millspaugh', email='andrew@alveare.io', password='foo'):
    from alveare.models import User
    user = User(first_name, last_name, email, password)
    db.session.add(user)
    return user

def create_one_manager(db, user=None):
    from alveare.models import Manager
    if not user:
        user = create_one_user(db)
    organization = create_one_organization(db)
    manager = Manager(user, organization)
    db.session.add(manager)
    return manager

def create_one_contractor(db, user=None):
    from alveare.models import Contractor, SkillSet
    if not user:
        user = create_one_user(db)
    contractor = Contractor(user)
    SkillSet(contractor)
    db.session.add(contractor)
    return contractor

def create_one_bank_account(db, owner):
    from alveare.models import BankAccount, Organization, Contractor
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
    from alveare.models import CodeClearance
    if not contractor:
        contractor = create_one_contractor(db)
    if not project:
        project = create_one_project(db)
    code_clearance = CodeClearance(project, contractor, pre_approved)
    db.session.add(code_clearance)
    return code_clearance

def create_one_remote_work_history(db, contractor=None):
    from alveare.models import RemoteWorkHistory
    if not contractor:
        contractor = create_one_contractor(db)
    remote_work_history = RemoteWorkHistory(contractor)
    db.session.add(remote_work_history)
    return remote_work_history

def create_one_github_account(db, remote_work_history=None, user_name='ravioli'):
    from alveare.models import GithubAccount
    if not remote_work_history:
        remote_work_history = create_one_remote_work_history(db)
    github_account = GithubAccount(remote_work_history, user_name)
    db.session.add(github_account)
    return github_account

def create_one_project(db, organization_name='Alveare', project_name='api'):
    from alveare.models import Organization, Project, CodeRepository
    organization = create_one_organization(db)
    project = Project(organization, project_name)
    code_repo = CodeRepository(project)
    db.session.add(organization)
    db.session.add(project)
    db.session.add(code_repo)
    return project

def create_one_remote_project(db, organization_name='Alveare', project_name='api'):
    from alveare.models import Organization, RemoteProject, CodeRepository
    organization = create_one_organization(db, organization_name)
    remote_project = RemoteProject(organization, project_name)
    code_repo = CodeRepository(remote_project)
    db.session.add(organization)
    db.session.add(remote_project)
    db.session.add(code_repo)
    return remote_project

def create_one_github_project(db, organization=None, project_name='api'):
    from alveare.models import Organization, GithubProject, CodeRepository
    if not organization:
        organization = create_one_organization(db, 'Alveare')
    github_project = GithubProject(organization, project_name)
    code_repo = CodeRepository(github_project)
    db.session.add(github_project)
    return github_project

def create_one_internal_ticket(db, title, description=None, project=None):
    from alveare.models import InternalTicket
    if not project:
        project = create_one_project(db)
    if not description:
        description = title + '-DESCRIPTION'
    ticket = InternalTicket(project, title, description)
    db.session.add(ticket)
    return ticket

def create_one_remote_ticket(db, title, description=None, project=None):
    from alveare.models import RemoteTicket, SkillRequirement
    if not project:
        project = create_one_project(db)
    if not description:
        description = title + '-DESCRIPTION'
    ticket = RemoteTicket(project, title, description)
    SkillRequirement(ticket)
    db.session.add(ticket)
    return ticket

def create_one_github_ticket(db, number, project=None):
    from alveare.models import GithubTicket, SkillRequirement
    if not project:
        project = create_one_github_project(db)
    ticket = GithubTicket(project, number)
    SkillRequirement(ticket)
    db.session.add(ticket)
    return ticket

def create_some_tickets(db, ticket_titles=None):
    from alveare.models import InternalTicket, RemoteTicket, SkillRequirement
    project = create_one_project(db)
    if not ticket_titles:
        ticket_titles = ['Foo', 'Bar', 'Baz', 'Qux']
    tickets = []
    for title in ticket_titles:
        ticket = InternalTicket(project, title)
        SkillRequirement(ticket)
        tickets.append(ticket)
    db.session.add_all(tickets)
    return tickets

def create_ticket_matches(db, tickets=None, contractor=None):
    from alveare.models import TicketMatch
    if not tickets:
        tickets = create_some_tickets(db)
    if not contractor:
        contractor = create_one_contractor(db)
    ticket_matches = []
    for ticket in tickets:
        ticket_matches.append(TicketMatch(contractor.skill_set, ticket.skill_requirement, 100))
    db.session.add_all(ticket_matches)
    return ticket_matches

def create_one_snapshot(db, ticket=None):
    from alveare.models import InternalTicket, TicketSnapshot, SkillRequirement
    if not ticket:
        ticket = InternalTicket(create_one_project(db), 'for a snapshot')
        SkillRequirement(ticket)
        db.session.add(ticket)
    ts = TicketSnapshot(ticket or InternalTicket(create_one_project(db), 'for a snapshot'))
    db.session.add(ts)
    return ts

def create_one_auction(db, tickets=None, duration=1000, finish_work_by=None, redundancy=1):
    if not finish_work_by:
        finish_work_by = datetime.datetime.now() + datetime.timedelta(days=2)
    from alveare.models import Auction, TicketSet, BidLimit, TicketSnapshot, TermSheet
    if not tickets:
        tickets = create_some_tickets(db)
    ticket_snaps = [TicketSnapshot(ticket) for ticket in tickets]
    bid_limits = [BidLimit(ticket_snap, 200) for ticket_snap in ticket_snaps]
    term_sheet = TermSheet('Some legal mumbo-jumbo')
    ticket_set = TicketSet(bid_limits)
    organization = tickets[0].project.organization
    auction = Auction(organization, ticket_set, term_sheet, duration, finish_work_by, redundancy)
    db.session.add(auction)
    return auction

def create_one_nomination(db, auction=None, contractor=None):
    from alveare.models import Nomination
    if not auction:
        auction = create_one_auction(db)
    if not contractor:
        contractor = create_one_contractor(db)
    nomination = Nomination(contractor, auction.ticket_set)
    db.session.add(nomination)
    return nomination

def create_one_job_fit(db, nomination=None, ticket_matches=None):
    from alveare.models import TicketMatch, JobFit
    if not nomination:
        nomination = create_one_nomination(db)
    skill_set = nomination.contractor.skill_set
    if not ticket_matches:
        ticket_matches = []
        for bid_limit in nomination.ticket_set.bid_limits:
            ticket_matches.append(TicketMatch(skill_set, bid_limit.ticket_snapshot.ticket.skill_requirement, 100))
    job_fit = JobFit(nomination, ticket_matches)
    db.session.add(job_fit)
    return job_fit

def create_one_feedback(db):
    from alveare.models import Feedback
    auction = create_one_auction(db)
    contractor = create_one_contractor(db)
    feedback = Feedback(auction, contractor, 'Your auction sucks')
    db.session.add(feedback)
    return feedback

def create_one_bid(db):
    from alveare.models import Bid, WorkOffer
    auction = create_one_auction(db)
    contractor = create_one_contractor(db)
    work_offers = []
    for bid_limit in auction.ticket_set.bid_limits:
        work_offers.append(WorkOffer(contractor, bid_limit.ticket_snapshot, 150))
    bid = Bid(auction, contractor)
    db.session.add(bid)
    return bid

def create_one_contract(db):
    from alveare.models import Contract
    bid = create_one_bid(db)
    contract = Contract(bid)
    db.session.add(bid)
    return contract

def create_some_work(db, review=True, debit_credit=True, mediation=True, arbitration=True):
    from alveare.models import Work, Review, Debit, Credit, Mediation, Arbitration
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
    from alveare.models import Review, Comment
    work = create_some_work(db, review=False).pop()
    review = Review(work, rating)
    comment = Comment(review, comment)
    db.session.add(review)
    return review

def create_admin_user(db, password):
    god = create_one_user(db, 'Flying', 'SpaghettiMonster', 'fsm@alveare.io', password)
    god.admin = True
    return god

def create_the_world(db):
    andrew = create_one_user(db, 'Andrew', 'Millspaugh', 'andrew@alveare.io')
    rapha = create_one_user(db, 'Raphael', 'Goyran', 'raphael@alveare.io')
    create_one_snapshot(db)
    create_one_snapshot(db)
    create_one_user(db, 'Steve', 'Gildred', 'steve@alveare.io')
    manager_andrew = create_one_manager(db, andrew) # also creates an organization
    manhattan_project = create_one_github_project(db, manager_andrew.organization, 'Manhattan')
    manhattan_tickets = [ create_one_github_ticket(db, ticket_number, manhattan_project) for ticket_number in range(10) ]
    rapha_contractor = create_one_contractor(db, rapha)
    andrew_contractor = create_one_contractor(db, andrew)
    manhattan_ticket_matches = create_ticket_matches(db, manhattan_tickets, rapha_contractor)
    manhattan_auction = create_one_auction(db, manhattan_tickets)
    rapha_nomination = create_one_nomination(db, manhattan_auction, rapha_contractor)
    andrew_nomination = create_one_nomination(db, manhattan_auction, andrew_contractor)
    rapha_manhattan_job_fit = create_one_job_fit(db, rapha_nomination, manhattan_ticket_matches)
    create_one_code_clearance(db, manhattan_project, rapha_contractor, pre_approved=True)
    create_one_code_clearance(db, manhattan_project, andrew_contractor, pre_approved=False)
    create_one_bank_account(db, rapha_contractor)
    rapha_rwh = create_one_remote_work_history(db, rapha_contractor)
    create_one_github_account(db, rapha_rwh, 'rapha.opensource')
    create_one_github_account(db, rapha_rwh, 'joe-la-mitraille')
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
