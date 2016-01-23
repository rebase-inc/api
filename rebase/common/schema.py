from functools import partialmethod

from flask.ext.login import current_user
from marshmallow import Schema, fields
from sqlalchemy.orm.collections import InstrumentedList

from rebase.common.exceptions import marshmallow_exceptions, NotFoundError, BadDataError
from rebase.common.keys import get_model_primary_keys
from rebase.memoize import in_process


class RebaseSchema(Schema):

    def load(self, *args, **kwargs):
        with marshmallow_exceptions(args[0]):
            return super().load(*args, **kwargs)

    def dump(self, *args, **kwargs):
        with marshmallow_exceptions(args[0]):
            return super().dump(*args, **kwargs)

    def _get_or_make_object(self, model, data):
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


# TODO implement incremental hashing
def _setitem(ilist, index, element):
    current_hash = getattr(ilist, '__current_hash__', 0)

def _hash(ilist):
    pile = ''
    for elt in ilist:
        pile = pile+str(elt)
    return hash(pile)

setattr(InstrumentedList, '__hash__', _hash)

class SecureNestedField(fields.Nested):
    def __init__(self, nested, strict=False, *args, **kwargs):
        self.strict = strict
        super().__init__(nested, *args, **kwargs)

    @in_process.memoize()
    def _serialize_with_user(self, nested_obj, attr, obj, user):
        if not nested_obj:
            if self.many:
                return []
            else:
                return None
        if not user:
            raise ValueError('Current user not supplied to {} nested on {}'.format(nested_obj, obj))
        if self.many:
            nested_obj = [elem for elem in nested_obj if elem.allowed_to_be_viewed_by(user)]
        else:
            nested_obj = nested_obj if nested_obj.allowed_to_be_viewed_by(user) else None
        self.schema.context = self.context
        return super()._serialize(nested_obj, attr, obj)

    _serialize = partialmethod(_serialize_with_user, user=current_user)

    @property
    def schema(self):
        _schema = fields.Nested.schema.fget(self)
        _schema.strict = self.strict
        _schema.context = {} # hack
        return _schema

