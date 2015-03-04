import datetime

def create_one_organization(db, name='Alveare'):
    from alveare.models import Organization
    organization = Organization(name)
    db.session.add(organization)
    return organization

def create_one_user(db, first_name='Andrew', last_name='Millspaugh', email='andrew@alveare.io'):
    from alveare.models import User
    user = User(first_name, last_name, email, 'hashedpassword')
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

def create_one_contractor(db):
    from alveare.models import Contractor, SkillSet
    user = create_one_user(db)
    contractor = Contractor(user)
    SkillSet(contractor)
    db.session.add(contractor)
    return contractor

def create_one_code_clearance(db):
    from alveare.models import CodeClearance
    contractor = create_one_contractor(db)
    project = create_one_project(db)
    code_clearance = CodeClearance(project, contractor)
    db.session.add(code_clearance)
    return code_clearance

def create_one_remote_work_history(db, contractor=None):
    from alveare.models import RemoteWorkHistory
    if not contractor:
        contractor = create_one_contractor(db)
    remote_work_history = RemoteWorkHistory(contractor)
    db.session.add(remote_work_history)
    return remote_work_history

def create_one_github_account(db, user_name='ravioli'):
    from alveare.models import GithubAccount
    remote_work_history = create_one_remote_work_history(db)
    github_account = GithubAccount(remote_work_history, user_name)
    db.session.add(github_account)
    return github_account

def create_one_project(db, organization_name='Alveare', project_name='api'):
    from alveare.models import Organization, Project, CodeRepository
    organization = Organization(organization_name)
    project = Project(organization, project_name)
    code_repo = CodeRepository(project)
    db.session.add(organization)
    db.session.add(project)
    db.session.add(code_repo)
    return project

def create_one_remote_project(db, organization_name='Alveare', project_name='api'):
    from alveare.models import Organization, RemoteProject, CodeRepository
    organization = Organization(organization_name)
    remote_project = RemoteProject(organization, project_name)
    code_repo = CodeRepository(remote_project)
    db.session.add(organization)
    db.session.add(remote_project)
    db.session.add(code_repo)
    return remote_project

def create_one_github_project(db, organization_name='Alveare', project_name='api'):
    from alveare.models import Organization, GithubProject, CodeRepository
    organization = Organization(organization_name)
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
    from alveare.models import RemoteTicket
    if not project:
        project = create_one_project(db)
    if not description:
        description = title + '-DESCRIPTION'
    ticket = RemoteTicket(project, title, description)
    db.session.add(ticket)
    return ticket

def create_one_github_ticket(db, number, project=None):
    from alveare.models import GithubTicket
    if not project:
        project = create_one_project(db)
    ticket = GithubTicket(project, number)
    db.session.add(ticket)
    return ticket

def create_some_tickets(db, ticket_titles=None):
    from alveare.models import InternalTicket, RemoteTicket, SkillRequirements
    project = create_one_project(db)
    if not ticket_titles:
        ticket_titles = ['Foo', 'Bar', 'Baz', 'Qux']
    tickets = []
    for title in ticket_titles:
        ticket = InternalTicket(project, title)
        SkillRequirements(ticket)
        tickets.append(ticket)
    db.session.add_all(tickets)
    return tickets

def create_ticket_matches(db):
    from alveare.models import TicketMatch
    tickets = create_some_tickets(db)
    contractor = create_one_contractor(db)
    ticket_matches = []
    for ticket in tickets:
        ticket_matches.append(TicketMatch(contractor.skill_set, ticket.skill_requirements, 100))
    db.session.add_all(ticket_matches)
    return ticket_matches

def create_one_auction(db, duration=1000, finish_work_by=None, redundancy=1):
    if not finish_work_by:
        finish_work_by = datetime.datetime.now() + datetime.timedelta(days=2)
    from alveare.models import Auction, TicketSet, BidLimit, TicketSnapshot, TermSheet
    tickets = create_some_tickets(db)
    ticket_snaps = [TicketSnapshot(ticket) for ticket in tickets]
    bid_limits = [BidLimit(ticket_snap, 200) for ticket_snap in ticket_snaps]
    term_sheet = TermSheet('Some legal mumbo-jumbo')
    ticket_set = TicketSet()
    for bid_limit in bid_limits:
        ticket_set.add_bid_limit(bid_limit)
    auction = Auction(ticket_set, term_sheet, duration, finish_work_by, redundancy)
    db.session.add(auction)
    return auction

def create_one_candidate(db):
    from alveare.models import Candidate
    auction = create_one_auction(db)
    contractor = create_one_contractor(db)
    candidate = Candidate(contractor, auction.ticket_set)
    db.session.add(candidate)
    return candidate

def create_one_job_fit(db):
    from alveare.models import TicketMatch, JobFit
    candidate = create_one_candidate(db)
    skill_set = candidate.contractor.skill_set
    ticket_matches = []
    for bid_limit in candidate.ticket_set.bid_limits:
        ticket_matches.append(TicketMatch(skill_set, bid_limit.snapshot.ticket.skill_requirements, 100))
    job_fit = JobFit(candidate, ticket_matches)
    db.session.add(job_fit)
    return job_fit

def create_one_feedback(db):
    from alveare.models import Feedback
    auction = create_one_auction(db)
    contractor = create_one_contractor(db)
    feedback = Feedback(auction, contractor)
    db.session.add(feedback)
    return feedback

def create_one_bid(db):
    from alveare.models import Bid, WorkOffer
    auction = create_one_auction(db)
    contractor = create_one_contractor(db)
    work_offers = []
    for bid_limit in auction.ticket_set.bid_limits:
        work_offers.append(WorkOffer(bid_limit.snapshot, 150))
    bid = Bid(auction, contractor, work_offers)
    db.session.add(bid)
    return bid

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

def create_the_world(db):
    u1 = create_one_user(db, 'Andrew', 'Millspaugh', 'andrew@alveare.io')
    create_one_user(db, 'Raphael', 'Goyran', 'raphael@alveare.io')
    create_one_user(db, 'Steve', 'Gildred', 'steve@alveare.io')
    create_one_manager(db, u1) # also creates an organization
    create_some_work(db)
    create_some_work(db, review=False)
    create_some_work(db, mediation=False)
    create_some_work(db, arbitration=False)
    create_some_work(db, debit_credit=False)
    create_one_work_review(db, 5, 'It was amazing')
    create_one_work_review(db, 3, 'Meh')
