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
        ticket = models.Ticket(title, description)
        ticket_snapshot = models.TicketSnapshot(ticket)
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snapshot, work_price)
        work = self.create_model(self.model, work_offer)

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
