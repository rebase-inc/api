from functools import partialmethod

from flask import current_app
from flask.ext.login import current_user
from marshmallow import Schema, fields
from sqlalchemy.orm.collections import InstrumentedList

from rebase.common.exceptions import marshmallow_exceptions, NotFoundError, BadDataError
from rebase.common.keys import get_model_primary_keys


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
    _result = 0
    for elt in ilist:
        _result ^= hash(elt)
    return _result

setattr(InstrumentedList, '__hash__', _hash)


def make_cache_key(_serialize, secure_nested_field, nested_obj, attr, obj, user):
    '''
    Returns a cache key for '_serialize' function call signature.
    Internally, that cache key is stored in cache.keys along with the parent of the object to be
    serialized.

    So cache.keys = { hash(nested_obj) : (cache_key, obj) }
    
    If nested_obj is a list (InstrumentedList), we save cache_key for each item in the list.
    This way, if an item gets invalidated, the whole list does too, and its parents.
    '''
    cache = current_app.cache_in_process
    cache_key = cache._memoize_make_cache_key()(_serialize, secure_nested_field, nested_obj, attr, obj, user)
    if nested_obj:
        _hash = hash(nested_obj)
        value = (cache_key, hash(obj))
        # only add new values to the keys cache
        if _hash not in cache.keys or value not in cache.keys[_hash]:
           cache.keys[_hash].add(value) 
        # for lists, make sure to add one cache entry per item in the list
        # in order to invalidate the whole list if any one item gets invalidated
        if secure_nested_field.many:
            _value = (cache_key, _hash)
            for elem in nested_obj:
                cache.keys[hash(elem)].add(_value)
    return cache_key


class SecureNestedField(fields.Nested):

    def __init__(self, nested, strict=False, *args, **kwargs):
        self.strict = strict
        super().__init__(nested, *args, **kwargs)

    @current_app.cache_in_process.memoize(timeout=3600)
    def _serialize_with_user(self, nested_obj, attr, obj, user):

        if not nested_obj:
            if self.many:
                return []
            else:
                return None
        current_app.cache_in_process.misses += 1
        if self.many:
            nested_obj = [elem for elem in nested_obj if elem.allowed_to_be_viewed_by(user)]
        else:
            nested_obj = nested_obj if nested_obj.allowed_to_be_viewed_by(user) else None
        self.schema.context = self.context
        return super()._serialize(nested_obj, attr, obj)

    _serialize_with_user.make_cache_key = make_cache_key

    _serialize = partialmethod(_serialize_with_user, user=current_user)

    @property
    def schema(self):
        _schema = fields.Nested.schema.fget(self)
        _schema.strict = self.strict
        _schema.context = {} # hack
        return _schema

