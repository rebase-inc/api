from .. import AlveareTestCase

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
