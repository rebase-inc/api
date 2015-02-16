import datetime

def create_one_organization(db, name='Alveare'):
    from alveare.models import Organization
    organization = Organization(name)
    db.session.add(organization)
    return organization

def create_one_contractor(db, first_name='Andrew', last_name='Millspaugh', email='andrew@alveare.io'):
    from alveare.models import Contractor, SkillSet
    contractor = Contractor(first_name, last_name, email, SkillSet())
    db.session.add(contractor)
    return contractor

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

def create_some_tickets(db, ticket_titles=None):
    from alveare.models import Ticket
    project = create_one_project(db)
    if not ticket_titles:
        ticket_titles = ['Foo', 'Bar', 'Baz', 'Qux']
    tickets = []
    for title in ticket_titles:
        tickets.append(Ticket(project, title))
        db.session.add(tickets[-1])
    return tickets

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

def create_one_talent_match(db, score=100):
    from alveare.models import TalentMatch
    auction = create_one_auction(db)
    contractor = create_one_contractor(db)
    talent_match = TalentMatch(contractor, auction.ticket_set, score)
    db.session.add(talent_match)
    return talent_match

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
    bid = Bid(auction, contractor)
    for bid_limit in auction.ticket_set.bid_limits:
        work_offer = WorkOffer(bid, bid_limit.snapshot, 150)
        db.session.add(work_offer)
    return bid

def create_some_work(db, review=True, debit_credit=True, mediation=True):
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
            _ = Arbitration(Mediation(work))
        db.session.add(work)
    return works

def create_one_work_review(db, rating, comment):
    from alveare.models import Review, Comment
    work = create_some_work(db, review=False).pop()
    review = Review(work, rating)
    comment = Comment(review, comment)
    db.session.add(review)
    return review

