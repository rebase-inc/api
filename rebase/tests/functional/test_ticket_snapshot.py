from copy import copy

from . import RebaseRestTestCase, RebaseNoMockRestTestCase
from rebase.tests.common.ticket_snapshot import (
    case_as_manager,
    case_past_work_as_contractor,
    case_auctions_as_contractor,
)
from rebase.common.utils import RebaseResource, validate_resource_collection

class TestTicketSnapshot(RebaseNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = RebaseResource(self, 'TicketSnapshot')

    def test_as_manager(self):
        mgr_user, snapshot = self._run(case_as_manager, 'manager')
        validate_resource_collection(self, [snapshot])
        snapshot_blob = self.resource.get(snapshot.id)
        del snapshot_blob['date']
        self.resource.update(**snapshot_blob)
        self.resource.delete(**snapshot_blob)
        new_snapshot = copy(snapshot_blob)
        del new_snapshot['id']
        self.resource.create(**new_snapshot)

    def test_as_contractor(self):
        contractor_user, snapshot = self._run(case_past_work_as_contractor, 'contractor')
        validate_resource_collection(self, [snapshot])
        snapshot_blob = self.resource.get(snapshot.id)
        self.resource.update(expected_status=401, **snapshot_blob)
        self.resource.delete(expected_status=401, **snapshot_blob)
        new_snapshot = copy(snapshot_blob)
        del new_snapshot['id']
        new_snapshot['ticket']['id'] = snapshot.ticket.id
        self.resource.create(expected_status=401, **new_snapshot)

        contractor_user, snapshot = self._run(case_auctions_as_contractor, 'contractor')
        validate_resource_collection(self, [snapshot])

    def test_as_anonymous(self):
        mgr_user, snapshot = self._run(case_as_manager, 'manager')
        self.logout()
        self.assertFalse(self.resource.get_all(401))
