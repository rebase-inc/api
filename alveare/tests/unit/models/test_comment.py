from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models

class TestCommentModel(AlveareModelTestCase):
    model = models.Comment

    def test_create(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        review = models.Review(work, 4)
        new_comment = self.create_model(self.model, review, 'Hello')
        self.assertEqual(new_comment.content, 'Hello')
        self.db.session.commit()

    def test_delete_parent(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        review = models.Review(work, 4)
        comment = self.create_model(self.model, review, 'Hello')
        self.assertEqual(comment.content, 'Hello')
        self.db.session.commit()

        self.delete_instance(review)
        with self.assertRaises(ObjectDeletedError):
            self.model.query.get(comment.id)

    def test_delete(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        review = models.Review(work, 4)
        comment = self.create_model(self.model, review, 'Bye')
        self.delete_instance(comment)
        self.assertNotEqual(models.Review.query.get(review.id), None)

    def test_update(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        review = models.Review(work, 4)
        new_comment = self.create_model(self.model, review, 'Foo')
        self.assertEqual(new_comment.content, 'Foo')

        new_comment.content = 'Bar'
        self.db.session.commit()

        modified_comment = self.model.query.get(new_comment.id)
        self.assertEqual(modified_comment.content, 'Bar')

    def test_bad_create(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        review = models.Review(work, 4)
        with self.assertRaises(InterfaceError):
            self.create_model(self.model, review, str)

