from datetime import datetime, timedelta
import uuid
from random import randint, randrange, sample, uniform, choice
from .utils import (
    pick_a_word,
    pick_a_first_name,
    pick_a_last_name,
    pick_an_organization_name,
)

from rebase.git.repo import Repo

FAKE_COMMENTS = [
    '@rapha, I\'m convinced that you were right regarding the composite primary keys being a better choice. However, in the few places where we are using composite primary keys right now, I don’t think the relationship is being properly referenced. See the SQLAlchemy documentation for proper reference of a composite foreign key.',
    'What do you mean? Is this not correct (from job_fit model)? ```__table_args__ = ( \n DB.ForeignKeyConstraint( [contractor_id, ticket_set_id], [Nomination.contractor_id, Nomination.ticket_set_id], ondelete=\'CASCADE\'), {})```',
    'Hmm, that _does_ *look* correct. The one I was looking at is in the bid model. It indirectly references the auction and contractor ids through the nomination model, though it doesn’t specifically reference the nomination model. This should instead be switched to a reference like above. I guess I should\'ve actually looked into the places where this was happening.',
    'I\'m pretty sure you can\'t do that. It just doesn\'t look right',
    'Where are you getting this idea from? I think it goes something like this ```\ndef foo():\n    return \'bar\'```',
    'Absolutely. I\'m pretty sure I can handle that',
    'Where do you get the extra fields for that one object?',
    'I don\'t know. Let me check on that and get back to you',
    'How about, instead, we just look at that other thing?',
    'I cannot highlight to copy/paste the data in the devtools default UI. It won\'t highlight the text on using chrome 47. This is intentional due to: : chibicode/react-json-tree#10',
    'I\'ve looked at #585 foobar/react#12 but can\'t seem to make my code work.  By console.log and redux devtools I can see that my state is successfully updated but there is no fresh render',
    'Maybe @jldfaster, @axlhaer, and @foolitt might want to take a look at this too.',
    '@faffnal there are already 2 examples ported : counter and shopping-cart; although there is no complex operations in the examples (added a simple example of onBoarding to the counter example; i\'ll try to port other examples later; it was on the roadmap anyway to provide more examples. I think we need some use cases involving non trivial operations (i mean other than simple reactions) that still can fit into small examples, perhaps some use case that someone found difficult to implement using thunks.',
    'I think foobar-effects and foobar-saga address 2 complementary concerns. I think redux-saga can also be used as a composition middleware for foobar-effects (unless I\'m mistaken) because it automatically resolve responses from dispatch calls.',
    'seems a bit hard to read, is there a better way to express not blocking?',
    'I was thinking the same thing. Maybe a helper function io.spawn which encapsulates the code above.',
    'I am advocating the Elm approach ever since the first time I encountered Flux and after 3 successful production projects (1 Flux, 2 Redux) I am still convinced that it\'s it the only right way to think about side effects and I am really convinced that I won\'t change my opinion in near future.',
    'Not sure if I correctely understood it; can you elaborate ?',
    'Could you write a unit test for this use case?',
    'I understand; that\'s why you emphasized the world \'unit\'. I can surely setup an integration test which connects the reducer and saga to some dispatcher, dispatches the action then checks the result of the 2 but of course this is not as simple as unit testing. Sure, pure functions will be always easier to test.',
    'added support for non blocking calls using fork and join',
    'API is shaping up nicely, great work. :+1:',
    '@loosnn I like what you\'re doing here as well. I think you are right that the most correct place for all this logic is in the middleware, so that you have a pristine log of intent. I\'m excited to see how this shapes up.',
]

FAKE_SKILLS = ['Python', 'SQLAlchemy', 'd3js', 'Marshmallow', 'docker', 'NLP', 'ML', 'unittest', 'Javascript', 'ES6', 'security']

FAKE_TICKETS = set([
    'Abstract out state machine event resource creation',
    'For all ORM relationships that reference a table with composite foreign key, combine those keys into one relationship.',
    'Add permission checking to rebase REST object creation and up date methods.',
    'Refactor auction ORM model to remove organization helper relationship.',
    'Add password secured fields to profile page',
    'Change bank account model initialization method to take a generic owner parameter.',
    'Do this one thing and then the other thing so we have more things to do.',
    'Play with the quadcopter for 10-15 hours.',
    'Refactor RQ server to handle jobs from different origins',
    'Enforce minimum entropy on user passwords',
    'Add forgotten password link to profile page',
    'Add logical separation between users that are developers and users that are managers',
    'Find method of better distributing work for ml platform among different servers',
    'Implement a higher order api for text sentiment processing',
    'Build better user onboarding flow',
    'Allow developer to input their own skill set instead of relying on github integration',
    'Add integration with Jira',
    'Add integration with Asana',
    'Add method for user to dynamically generate docker images for deployment of new tasks'
])


def create_one_organization(db, name=None, user=None):
    from rebase.models import Organization
    user = user or create_one_user(db)
    organization = Organization(name or pick_an_organization_name(), user)
    db.session.add(organization)
    return organization

def create_one_user(db, name=None, email=None, password='foo', admin=False):
    from rebase.models import User
    email = email or 'user-{}@rebase.io'.format(uuid.uuid4())
    user = User(
        name or pick_a_first_name() + pick_a_last_name(),
        email,
        password
    )
    user.admin = admin
    db.session.add(user)
    return user

def create_one_manager(db, user=None, project=None):
    from rebase.models import Manager
    user = user or create_one_user(db)
    project = project or create_one_project(db)
    manager = Manager(user, project)
    db.session.add(manager)
    return manager

def create_one_owner(db, user=None, org=None):
    from rebase.models import Owner
    user = user or create_one_user(db)
    org = org or create_one_organization(db)
    owner = Owner(user, org)
    db.session.add(owner)
    return owner

def create_one_contractor(db, user=None):
    from rebase.models import Contractor, SkillSet
    user = user or create_one_user(db)
    contractor = Contractor(user)
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

def create_one_project(db, organization=None, project_name=None):
    from rebase.models import Organization, InternalProject
    organization = organization or create_one_organization(db)
    project = InternalProject(organization, project_name or pick_a_word().capitalize()+' Project')
    db.session.add(project)
    db.session.commit()
    repo = Repo(project)
    repo.create_internal_project_repo(project.managers[0].user)
    return project

def create_one_remote_project(db, organization=None, project_name=None):
    from rebase.models import RemoteProject
    organization = organization or create_one_organization(db)
    remote_project = RemoteProject(organization, project_name or pick_a_word().capitalize()+' Project')
    db.session.add(remote_project)
    return remote_project

def create_one_github_project(db, organization=None, project_name=None):
    from rebase.models import Organization, GithubProject
    organization = organization or create_one_organization(db)
    github_project = GithubProject(organization, project_name or pick_a_word().capitalize()+' Project')
    db.session.add(github_project)
    return github_project

def create_one_internal_ticket(db, title=None, description=None, project=None, created=None):
    from rebase.models import InternalTicket, SkillRequirement, Comment
    project = project or create_one_project(db)
    title = title or ' '.join(pick_a_word() for i in range(5))
    description = description or ' '.join(pick_a_word() for i in range(5))
    ticket = InternalTicket(project, title)
    user = project.managers[0].user
    #Comment(user, description, ticket=ticket)
    SkillRequirement(ticket)
    if created:
        ticket.created = created
    db.session.add(ticket)
    return ticket

def create_one_github_ticket(db, number=None, title=None, project=None):
    from rebase.models import GithubTicket, SkillRequirement
    number = number or randrange(1, 99999)
    project = project or create_one_github_project(db)
    title = title or pick_a_word().capitalize()+' '+' '.join([pick_a_word() for i in range(5)])
    ticket = GithubTicket(project, number, title=title, created=datetime.now())
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

def create_one_auction(db, tickets=None, duration=1000, finish_work_by=None, redundancy=1, price=200):
    finish_work_by = finish_work_by or datetime.now() + timedelta(days=2)
    from rebase.models import Auction, TicketSet, BidLimit, TicketSnapshot, TermSheet
    tickets = tickets or create_some_tickets(db)
    ticket_snaps = [TicketSnapshot(ticket) for ticket in tickets]
    bid_limits = [BidLimit(ticket_snap, price) for ticket_snap in ticket_snaps]
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
    # verify it doesn't already exist..
    nomination = Nomination.query.filter(Nomination.contractor==contractor).filter(Nomination.ticket_set==auction.ticket_set).first()
    if not nomination:
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
    job_fit = JobFit.query.filter_by(contractor_id=nomination.contractor_id, ticket_set_id=nomination.ticket_set_id).first()
    if not job_fit:
        job_fit = JobFit(nomination, ticket_matches)
    db.session.add(job_fit)
    return job_fit

def create_one_feedback(db, auction=None, contractor=None, comment=None):
    from rebase.models import Feedback, Comment

    feedback = Feedback(
        auction or create_one_auction(db),
        contractor or create_one_contractor(db)
    )
    Comment(feedback.contractor.user, comment or 'Your auction sucks', feedback=feedback)
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
    bid = Bid(auction, contractor, work_offers)
    db.session.add(bid)
    return bid

def create_one_contract(db):
    from rebase.models import Contract
    bid = create_one_bid(db)
    contract = Contract(bid)
    db.session.add(bid)
    return contract

def create_some_work(db, review=False, debit_credit=True, mediation=True, arbitration=True):
    from rebase.models import Work, Review, Debit, Credit, Mediation, Arbitration
    bid = create_one_bid(db)
    works = []
    for work_offer in bid.work_offers:
        work = Work(work_offer)
        works.append(work)
        if review:
            _ = Review(work)
        if debit_credit:
            _ = Debit(work, 100)
            _ = Credit(work, 120)
        if mediation:
            m = Mediation(work)
            if arbitration:
                _ = Arbitration(m)
        db.session.add(work)
    return works

def create_one_work_review(db, user, rating, comment):
    from rebase.models import Review, Comment
    work = create_some_work(db, review=False).pop()
    review = Review(work)
    review.rating = rating
    comment = Comment(user, comment, review=review)
    db.session.add(review)
    return review

def create_admin_user(db, password):
    god = create_one_user(db, 'Flying SpaghettiMonster', 'fsm@rebase.io', password)
    god.admin = True
    return god


class DeveloperUserStory(object):
    def __init__(self, db, name, email, password):
        self.name = name
        self.email = email
        self.password = password

        from rebase.models import Comment
        self.user = create_one_user(db, self.name, self.email, self.password, admin=False)
        user_ted = create_one_user(db, 'Ted Crisp', 'tedcrisp@joinrebase.com')
        org_veridian = create_one_organization(db, 'veridian', user_ted)
        project_matchmaker = create_one_project(db, org_veridian, 'matchmaker')
        manager_ted = project_matchmaker.managers[0]
        the_tickets = [create_one_internal_ticket(db, fake_ticket, project=project_matchmaker) for fake_ticket in FAKE_TICKETS]
        for ticket in the_tickets:
            for fake_comment in FAKE_COMMENTS:
                Comment(user_ted, fake_comment, ticket=ticket)
        self.contractor = create_one_contractor(db, self.user)
        code_clearance = create_one_code_clearance(db, project_matchmaker, self.contractor)
        the_matches = create_ticket_matches(db, the_tickets, self.contractor)
        the_auctions = [create_one_auction(db, [ticket]) for ticket in the_tickets]
        the_nominations = [create_one_nomination(db, auction, self.contractor, False) for auction in the_auctions]
        the_job_fits = [create_one_job_fit(db, nomination, [match]) for nomination, match in zip(the_nominations, the_matches)]

class ManagerUserStory(object):
    def __init__(self, db, name, email, password):
        self.name = name
        self.email = email
        self.password = password

        from rebase.models import Comment, SkillSet, SkillRequirement, TicketMatch, JobFit
        self.user = create_one_user(db, self.name, self.email, self.password, admin=False)
        devs = []
        devs.append(create_one_user(db, 'Andy Dwyer', 'andy@joinrebase.com'))
        devs.append(create_one_user(db, 'April Ludgate', 'april@joinrebase.com'))
        devs.append(create_one_user(db, 'Leslie Knope', 'leslie@joinrebase.com'))
        devs.append(create_one_user(db, 'Donna Meagle', 'donna@joinrebase.com'))
        devs.append(create_one_user(db, 'Tom Haverford', 'tom@joinrebase.com'))
        devs.append(create_one_user(db, 'Chris Traeger', 'chris@joinrebase.com'))
        devs.append(create_one_user(db, 'Jean-Ralphio Saperstein', 'jean-ralphio@joinrebase.com'))
        devs.append(create_one_user(db, 'Jerry Gergich', 'jerry@joinrebase.com'))
        devs.append(create_one_user(db, 'Ben Wyatt', 'ben@joinrebase.com'))
        devs.append(create_one_user(db, 'Ann Perkins', 'ann@joinrebase.com'))
        devs.append(create_one_user(db, 'Mark Brendanawicz', 'mark@joinrebase.com'))
        devs.append(create_one_user(db, 'Craig Middlebrooks', 'craig@joinrebase.com'))
        the_contractors = [create_one_contractor(db, user) for user in devs]
        skill_sets = []
        for contractor in the_contractors:
            skills = sample(FAKE_SKILLS, randint(3,6))
            skill_sets.append(SkillSet(contractor, {skill: uniform(0.2, 1.0) for skill in skills}))
        organization = create_one_organization(db, 'Parks and Recreation', self.user)
        project = create_one_project(db, organization, 'Lot 48')
        mgr = project.managers[0]
        the_new_tickets = [create_one_internal_ticket(db, fake_ticket, project=project, created=datetime.now() + timedelta(hours=randint(-72,0))) for fake_ticket in FAKE_TICKETS]
        
        for ticket in the_new_tickets:
            for fake_comment in sample(FAKE_COMMENTS, randint(2, 5)):
                Comment(choice([self.user] + devs), fake_comment, ticket=ticket)
            skills_required = sample(FAKE_SKILLS, randint(3,6))
            approx_skill = uniform(0.3, 1.0) # this is so the dev looks roughly uniformly skilled
            SkillRequirement(ticket, {skill: uniform(min(0.0, approx_skill - 0.2), min(1.0, approx_skill, + 0.2)) for skill in skills_required})

def create_the_world(db):
    andrew = create_one_user(db, 'Andrew Millspaugh', 'andrew@manager.rebase.io')
    rapha = create_one_user(db, 'Raphael Goyran', 'raphael@rebase.io')
    joe = create_one_user(db, 'Joe Pesci', 'joe@rebase.io')
    tim = create_one_user(db, 'Tim Pesci', 'tim@rebase.io')
    steve = create_one_user(db, 'Steve Gildred', 'steve@rebase.io')
    bigdough_project = create_one_github_project(db, project_name='Big Dough')
    internal_project = create_one_project(db)
    internal_project_tickets = [create_one_internal_ticket(db, 'Issue #{}'.format(i), project=internal_project) for i in range(10)]

    manhattan_project = create_one_github_project(db, project_name='Manhattan')
    manhattan_tickets = [ create_one_github_ticket(db, number=ticket_number, project=manhattan_project) for ticket_number in range(10) ]
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
    create_one_feedback(db)
    create_one_feedback(db)
    create_one_contract(db)
    create_one_contract(db)
    create_some_work(db)
    create_some_work(db, review=False)
    create_some_work(db, mediation=False)
    create_some_work(db, arbitration=False)
    create_some_work(db, debit_credit=False)
    create_one_work_review(db, andrew, 5, 'It was amazing')
    create_one_work_review(db, andrew, 3, 'Meh')
