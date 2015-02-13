import datetime

from .. import AlveareTestCase
from alveare import models

class AlveareModelTestCase(AlveareTestCase):

    def create_model(self, model, *args, **kwargs):
        instance = model(*args, **kwargs)
        self.db.session.add(instance)
        self.db.session.commit()

        self.assertNotEqual(model.query.get(instance.id), None)
        return instance

    def delete_instance(self, model, instance):
        self.db.session.delete(instance)
        self.db.session.commit()

        self.assertEqual(model.query.get(instance.id), None)

    def create_work(self, title, description, work_price=100, rating=None, debit=None, credit=None, mediation_rounds=0):
        work_offer = self.create_work_offer(title, description, work_price)
        work = models.Work(work_offer)

        if rating != None:
            models.Review(work, rating)
        if debit != None:
            models.Debit(work, debit)
        if credit != None:
            models.Credit(work, credit)
        for mediation_round in range(mediation_rounds):
            models.Arbitration(models.Mediation(work))

        self.db.session.add(work)
        return work

    def create_arbitration(self):
        work = self.create_work('dontcare', 'dontcare', 666, mediation_rounds=1)
        return work.mediation_rounds.one().arbitration

    def create_mediation(self):
        work = self.create_work('dontcare', 'dontcare', 666, mediation_rounds=1)
        return work.mediation_rounds.one()

    def create_review(self, rating, comment=None):
        work = self.create_work('dontcare', 'dontcare', 666, rating=rating)
        if comment:
            _ = models.Comment(work.review, comment)
        return work.review

    def create_debit_and_credit(self, debit_price, credit_price):
        work = self.create_work('dontcare', 'dontcare', 666, debit=debit_price, credit=credit_price)
        return (work.debit, work.credit)

    def create_work_offer(self, title, description, work_price):
        project = self.create_project('dontcare', 'dontcare')
        ticket = models.Ticket(project, title, description)
        ticket_snapshot = models.TicketSnapshot(ticket)
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snapshot, work_price)
        self.db.session.add(work_offer)
        return work_offer

    def create_bid(self, tickets):
        ''' tickets is a list of (title, description, price) '''
        bid = models.Bid()

        project = self.create_project('dontcare', 'dontcare')
        for title, description, price in tickets:
            ticket = models.Ticket(project, title, description)
            ticket_snap = models.TicketSnapshot(ticket)
            work_offer = models.WorkOffer(bid, ticket_snap, price)
        self.db.session.add(bid)
        return bid

    def create_organization(self, name):
        organization = models.Organization(name)
        self.db.session.add(organization)
        return organization

    def create_code_repository(self):
        project = self.create_project('dontcare','dontcare')
        repo = models.CodeRepository(project)
        self.db.session.add(repo)
        return repo

    def create_project(self, organization_name, project_name):
        organization = self.create_organization(organization_name)
        project = models.Project(project_name, organization)
        models.CodeRepository(project)
        self.db.session.add(project)
        return project

    def create_bid_limit(self, price):
        project = self.create_project('dontcare', 'dontcare')
        ticket = models.Ticket(project, 'dontcare', 'dontcare')
        bid_limit = models.BidLimit(ticket, price)
        self.db.session.add(bid_limit)
        return bid_limit

    def create_ticket(self, title, description):
        project = self.create_project('dontcare', 'dontcare')
        ticket = models.Ticket(project, title, description)
        return ticket

    def create_auction(self, tickets, terms, duration, finish_by, redundancy=1):
        ticket_list = []
        for title, description, price in tickets:
            ticket_list.append((self.create_ticket(title, description), price))
        term_sheet = models.TermSheet(terms)
        auction = models.Auction(ticket_list, term_sheet, duration, finish_by, redundancy)
        self.db.session.add(auction)
        return auction



