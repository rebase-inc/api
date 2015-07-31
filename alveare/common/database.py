#!/usr/bin/env python
from marshmallow import fields
from flask.ext.sqlalchemy import SQLAlchemy
from alveare.common.exceptions import BadDataError, NotFoundError
DB = SQLAlchemy()
DB_PRODUCTION_NAME = 'rebase'
DB_TEST_NAME = 'test_'+DB_PRODUCTION_NAME

def get_or_make_object(model, data, id_fields=None):
    id_fields = id_fields or ['id']
    instance_id = tuple(data.get(id_field) for id_field in id_fields)
    if all(instance_id):
        instance = model.query.get(instance_id)
        if not instance:
            raise NotFoundError(model.__tablename__, instance_id)
        return instance
    elif not data:
        raise BadDataError(model_name=model.__tablename__)
    return model(**data)

class SecureNestedField(fields.Nested):
    def _serialize(self, nested_obj, attr, obj):
        if not nested_obj:
            if self.many:
                return []
            else:
                return None
        current_user = self.context.get('current_user')
        if not current_user:
            raise ValueError('current_user not supplied to {} nested on {}'.format(nested_obj, obj))
        if self.many:
            nested_obj = [elem for elem in nested_obj if elem.allowed_to_be_viewed_by(current_user)]
        else:
            nested_obj = nested_obj if nested_obj.allowed_to_be_viewed_by(current_user) else None
        self.schema.context = self.context
        return super()._serialize(nested_obj, attr, obj)

class PermissionMixin(object):
    @classmethod
    def query_by_user(cls, user):
        msg = 'query_by_user not implemented for {}'.format(cls.__name__)
        raise NotImplementedError(msg.format(cls.__name__))

    def allowed_to_be_created_by(self, user):
        msg = 'allowed_to_be_created_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_modified_by(self, user):
        msg = 'allowed_to_be_modified_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_deleted_by(self, user):
        msg = 'allowed_to_be_deleted_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_viewed_by(self, user):
        msg = 'allowed_to_be_viewed_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

def query_by_user_or_id(cls, query_fn, filter_by_id, user, instance=None):
    if user.admin:
        query = cls.query
    else:
        query = query_fn(user)
    if instance:
        query = instance.filter_by_id(query)
    return query
