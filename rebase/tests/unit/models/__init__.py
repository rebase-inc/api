import datetime

from .. import RebaseTestCase
from datetime import datetime
from rebase import models

class RebaseModelTestCase(RebaseTestCase):

    def create_model(self, model, *args, **kwargs):
        instance = model(*args, **kwargs)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def delete_instance(self, instance):
        self.db.session.delete(instance)
        self.db.session.commit()

