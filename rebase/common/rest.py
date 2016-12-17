from copy import copy

from flask import jsonify, request
from flask_login import current_user, current_app

from rebase.common.exceptions import NotFoundError
from rebase.common.database import DB


def get_collection(model, serializer, role_id, handlers=None):
    '''
    model is the rebase resource to be queried and serialized
    serializer is a marshmallow Schema
    handlers is an optional dict of handlers for the following events:

    'pre_serialization': after the data has been queried from the DB,
    but before it is serialized in the response, this handler will be called with 
    and passed in the queried data.
    The handler must return a list of potentially updated instances.
    '''
    query = model.query_by_user(current_user)
    all_instances = query.limit(100).all()
    if handlers and 'pre_serialization' in handlers.keys():
        all_instances = handlers['pre_serialization'](all_instances)
    serializer.context = dict(current_user = current_user)
    return jsonify(**{model.__pluralname__: serializer.dump(all_instances, many=True).data})


def add_to_collection(model, deserializer, serializer, handlers=None):
    '''
    model is the rebase resource to be queried and serialized.
    serializer and deserializer are marshmallow Schemas.
    handlers is an optional dict of handlers for the following events:

    'pre_serialization': after the data has been committed to the DB,
    but before it is serialized in the response, this handler will be called with 
    and passed in the committed instance.
    The handler must return a potentially updated instance.
    '''
    pre_load_keys = copy(list(DB.session.identity_map.keys()))
    new_instance = deserializer.load(request.json or request.form).data
    DB.session.add(new_instance)
    if not new_instance.allowed_to_be_created_by(current_user):
        return current_app.login_manager.unauthorized()
    DB.session.commit()
    post_load_keys = copy(list(DB.session.identity_map.keys()))
    diff_keys = set(post_load_keys) - set(pre_load_keys)
    if handlers and 'pre_serialization' in handlers.keys():
        new_instance = handlers['pre_serialization'](new_instance)
    serializer.context = dict(current_user = current_user)
    response = jsonify(**{model.__tablename__: serializer.dump(new_instance).data})
    response.status_code = 201
    return response


def get_resource(model, instance_id, serializer, handlers=None):
    instance = model.query.get(instance_id)
    if not instance:
        raise NotFoundError(model.__tablename__, instance_id)
    if not instance.allowed_to_be_viewed_by(current_user):
        return current_app.login_manager.unauthorized()
    if handlers and 'pre_serialization' in handlers.keys():
        instance = handlers['pre_serialization'](instance)
    serializer.context = dict(current_user = current_user)
    return jsonify(**{model.__tablename__: serializer.dump(instance).data})


def update_resource(model, instance_id, update_deserializer, serializer, handlers=None):
    instance = model.query.get(instance_id)
    if not instance:
        raise NotFoundError(model.__tablename__, instance_id)
    if not instance.allowed_to_be_modified_by(current_user):
        return current_app.login_manager.unauthorized()
    fields_to_update = update_deserializer.load(request.form or request.json).data
    for field, value in fields_to_update.items():
        if getattr(instance, field) != value:
            setattr(instance, field, value)
    DB.session.add(instance)
    DB.session.commit()
    if handlers and 'pre_serialization' in handlers.keys():
        instance = handlers['pre_serialization'](instance)
    serializer.context = dict(current_user = current_user)
    response = jsonify(**{model.__tablename__: serializer.dump(instance).data})
    return response


def delete_resource(model, instance_id, handlers=None):
    instance = model.query.get(instance_id)
    if not instance:
        raise NotFoundError(model.__tablename__, instance_id)
    if not instance.allowed_to_be_deleted_by(current_user):
        return current_app.login_manager.unauthorized()
    if handlers and 'before_delete' in handlers.keys():
        instance = handlers['before_delete'](instance)
    DB.session.delete(instance)
    DB.session.commit()
    if handlers and 'pre_serialization' in handlers.keys():
        handlers['pre_serialization']()

    response = jsonify(message = '{} succesfully deleted'.format(model.__tablename__))
    response.status_code = 200
    if handlers and 'modify_response' in handlers.keys():
        response = handlers['modify_response'](response)
    return response


