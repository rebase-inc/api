from .. import AlveareTestCase

class AlveareModelTestCase(AlveareTestCase):

    def create_model(self, model, *args, **kwargs):
        self.db.session.add(model(*args))
        self.db.session.commit()

        all_instances = model.query.all()
        self.assertEqual(len(all_instances), 1)

        return all_instances.pop()

    def delete_instance(self, model, instance):
        self.db.session.delete(instance)
        self.db.session.commit()

        self.assertEqual(model.query.get(instance.id), None)
