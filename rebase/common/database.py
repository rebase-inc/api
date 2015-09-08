#!/usr/bin/env python
from marshmallow import fields
from flask.ext.login import current_user
from flask.ext.sqlalchemy import SQLAlchemy
from rebase.common.exceptions import (
    BadDataError,
    NotFoundError,
    AsContractorPathUndefined,
    AsManagerPathUndefined,
)
from rebase.common.query import query_from_class_to_user


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
        if not current_user:
            raise ValueError('current_user not supplied to {} nested on {}'.format(nested_obj, obj))
        if self.many:
            nested_obj = [elem for elem in nested_obj if elem.allowed_to_be_viewed_by(current_user)]
        else:
            nested_obj = nested_obj if nested_obj.allowed_to_be_viewed_by(current_user) else None
        self.schema.context = self.context
        return super()._serialize(nested_obj, attr, obj)

class PermissionMixin(object):
    as_contractor_path = None
    as_manager_path = None

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

    @classmethod
    def query_from_class_to_user(klass, path, user):
        query = klass.query
        for node in path:
            query = query.join(node)
        query = query.filter((path[-1].user if path else klass.user) == user)
        return query

    @classmethod
    def as_contractor(cls, user):
        if not cls.as_contractor_path:
            raise AsContractorPathUndefined(cls)
        return cls.query_from_class_to_user(cls.as_contractor_path, user)

    @classmethod
    def as_manager(cls, user):
        if not cls.as_manager_path:
            raise AsManagerPathUndefined(cls)
        return cls.query_from_class_to_user(cls.as_manager_path, user)

    @classmethod
    def role_to_query_fn(cls, user):
        if user.current_role.type == 'manager':
            return cls.as_manager
        elif user.current_role.type == 'contractor':
            return cls.as_contractor
        else:
            raise UnknownRole(user.current_role)

    @classmethod
    def query_by_user(cls, user):
        if user.is_admin():
            return cls.query
        return cls.role_to_query_fn(user)(user)

    @classmethod
    def setup_queries(cls, _):
        msg = 'setup_queries is not implemented for {}'
        #raise NotImplemented(msg.format(cls.__name__))
        #print(msg.format(cls.__name__))


def query_by_user_or_id(cls, query_fn, filter_by_id, user, instance=None):
    if user.admin:
        query = cls.query
    else:
        query = query_fn(user)
    if instance:
        query = instance.filter_by_id(query)
    return query
