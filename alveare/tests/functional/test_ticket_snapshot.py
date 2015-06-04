from copy import copy

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from alveare.tests.common.ticket_snapshot import (
    case_as_manager,
    case_past_work_as_contractor,
    case_auctions_as_contractor,
)
from alveare.common.utils import AlveareResource, validate_resource_collection

class TestTicketSnapshot(AlveareNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = AlveareResource(self, 'TicketSnapshot')

    def test_as_manager(self):
        mgr_user, snapshot = case_as_manager(self.db)
        validate_resource_collection(self, mgr_user, [snapshot])
        snapshot_blob = self.resource.get(snapshot.id)
        del snapshot_blob['date']
        self.resource.update(**snapshot_blob)
        self.resource.delete(**snapshot_blob)
        new_snapshot = copy(snapshot_blob)
        del new_snapshot['id']
        self.resource.create(**new_snapshot)

    def test_as_contractor(self):
        contractor_user, snapshot = case_past_work_as_contractor(self.db)
        validate_resource_collection(self, contractor_user, [snapshot])
        snapshot_blob = self.resource.get(snapshot.id)
        self.resource.update(expected_status=401, **snapshot_blob)
        self.resource.delete(expected_status=401, **snapshot_blob)
        new_snapshot = copy(snapshot_blob)
        del new_snapshot['id']
        new_snapshot['ticket']['id'] = snapshot.ticket.id
        self.resource.create(expected_status=401, **new_snapshot)

        contractor_user, snapshot = case_auctions_as_contractor(self.db)
        validate_resource_collection(self, contractor_user, [snapshot])

    def test_as_anonymous(self):
        mgr_user, snapshot = case_as_manager(self.db)
        self.logout()
        self.assertFalse(self.resource.get_all(401))
