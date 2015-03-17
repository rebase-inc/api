from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip

class TestTermSheetResource(AlveareRestTestCase):
    def setUp(self):
        self.resource = AlveareResource(self, 'TermSheet')
        super().setUp()

    def test_get_one(self):
        term_sheet = self.resource.get_any()
        self.assertTrue(term_sheet)
        self.assertTrue(term_sheet.pop('id'))
        self.assertIsInstance(term_sheet.pop('legalese'), str)
        self.assertEqual(term_sheet, {})

    @skip('term sheet are immutable')
    def test_update(self):
        pass

    def test_delete(self):
        self.resource.delete_any()

    @skip('term_sheet doesnt depend on any other resource')
    def test_delete_auction(self):
        term_sheet = self.resource.get_any()
        self.delete_resource('auction/{}'.format(term_sheet['auction']))
        self.get_resource(self.resource.url(term_sheet), 404)
