from marshmallow import Schema
from rebase.common.exceptions import marshmallow_exceptions, NotFoundError, BadDataError
from rebase.common.database import get_model_primary_keys

class RebaseSchema(Schema):

    def load(self, *args, **kwargs):
        with marshmallow_exceptions(args[0]):
            return super().load(*args, **kwargs)

    def dump(self, *args, **kwargs):
        with marshmallow_exceptions(args[0]):
            return super().dump(*args, **kwargs)

    def _get_or_make_object(self, model, data):
        print('trying to get or make object ' + str(model) + ' with data ' + str(data))
        if self.context.get('raw'): 
            return data
        primary_keys = get_model_primary_keys(model)
        instance_id = tuple(data.get(primary_key) for primary_key in primary_keys)
        if all(instance_id):
            instance = model.query.get(instance_id)
            if not instance:
                raise NotFoundError(model.__tablename__, instance_id)
            return instance
        elif not data:
            raise BadDataError(model_name=model.__tablename__)
        return model(**data)


