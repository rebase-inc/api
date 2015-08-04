from . import RebaseRestTestCase
from rebase.common.utils import RebaseResource
from unittest import skip

class TestTermSheetResource(RebaseRestTestCase):
    def setUp(self):
        self.resource = RebaseResource(self, 'TermSheet')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        term_sheet = self.resource.get_any()
        self.assertTrue(term_sheet)
        self.assertTrue(term_sheet.pop('id'))
        self.assertIsInstance(term_sheet.pop('legalese'), str)
        self.assertEqual(term_sheet, {})

    @skip('term sheet are immutable')
    def test_update(self):
        self.login_admin()
        pass

    def test_delete(self):
        self.login_admin()
        self.resource.delete_any()

    @skip('term_sheet doesnt depend on any other resource')
    def test_delete_auction(self):
        self.login_admin()
        term_sheet = self.resource.get_any()
        self.delete_resource('auction/{}'.format(term_sheet['auction']))
        self.get_resource(self.resource.url(term_sheet), 404)
