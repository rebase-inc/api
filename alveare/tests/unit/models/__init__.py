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

    def create_work(self, title, description, work_price=100, review=None, debit=None, credit=None, mediation_rounds=0):
        work_offer = self.create_work_offer(title, description, work_price)
        work = self.create_model(models.Work, work_offer)

        if review:
            _ = models.Review(work, review)
        if debit:
            _ = models.Debit(work, debit)
        if credit:
            _ = models.Credit(work, credit)
        for mediation_round in range(mediation_rounds):
            _ = models.Arbitration(models.Mediation(work))

        self.db.session.add(work)
        self.db.session.commit()
        return work

    def create_arbitration(self):
        work = self.create_work('dontcare', 'dontcare', 666, mediation_rounds=1)
        return work.mediation_rounds.one().arbitration

    def create_mediation(self):
        work = self.create_work('dontcare', 'dontcare', 666, mediation_rounds=1)
        return work.mediation_rounds.one()

    def create_review(self, rating, comment=None):
        work = self.create_work('dontcare', 'dontcare', 666, review=rating)
        if comment:
            _ = models.Comment(work.review, comment)
            self.db.session.commit()
        return work.review

    def create_debit_and_credit(self, debit_price, credit_price):
        work = self.create_work('dontcare', 'dontcare', 666, debit=debit_price, credit=credit_price)
        return (work.debit, work.credit)

    def create_work_offer(self, title, description, work_price):
        ticket = models.Ticket(title, description)
        ticket_snapshot = models.TicketSnapshot(ticket)
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snapshot, work_price)
        self.db.session.add(work_offer)
        self.db.session.commit()
        return work_offer
