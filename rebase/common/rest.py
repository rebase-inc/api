from flask import jsonify, request
from flask.ext.login import current_user, current_app
from rebase.common.exceptions import NotFoundError
from rebase.common.database import DB

def get_collection(model, serializer, pre_serialization=None):
    '''
    model is the rebase resource to be queried and serialized
    serializer is a marshmallow Schema
    pre_serialization is an optional handler called just before serialization.
    It takes as input the queries list of instances of that resource
    and returns a list of potentially updated instances.
    '''
    query = model.query_by_user(current_user)
    all_instances = query.limit(100).all()
    if pre_serialization:
        all_instances = pre_serialization(all_instances)
    serializer.context = dict(current_user = current_user)
    return jsonify(**{model.__pluralname__: serializer.dump(all_instances, many=True).data})

def add_to_collection(model, deserializer, serializer):
    new_instance = deserializer.load(request.json or request.form).data
    DB.session.add(new_instance)
    if not new_instance.allowed_to_be_created_by(current_user):
        return current_app.login_manager.unauthorized()
    DB.session.commit()
    serializer.context = dict(current_user = current_user)
    response = jsonify(**{model.__tablename__: serializer.dump(new_instance).data})
    response.status_code = 201
    return response

def get_resource(model, instance_id, serializer):
    instance = model.query.get(instance_id)
    if not instance:
        raise NotFoundError(model.__tablename__, instance_id)
    if not instance.allowed_to_be_viewed_by(current_user):
        return current_app.login_manager.unauthorized()
    serializer.context = dict(current_user = current_user)
    return jsonify(**{model.__tablename__: serializer.dump(instance).data})

def update_resource(model, instance_id, update_deserializer, serializer, pre_serialization=None):
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
    serializer.context = dict(current_user = current_user)
    if pre_serialization:
        instance = pre_serialization(instance)
    return jsonify(**{model.__tablename__: serializer.dump(instance).data})

def delete_resource(model, instance_id, modify_response=None):
    instance = model.query.get(instance_id)
    if not instance:
        raise NotFoundError(model.__tablename__, instance_id)
    if not instance.allowed_to_be_deleted_by(current_user):
        return current_app.login_manager.unauthorized()
    DB.session.delete(instance)
    DB.session.commit()

    response = jsonify(message = '{} succesfully deleted'.format(model.__tablename__))
    response.status_code = 200
    if modify_response:
        response = modify_response(response)
    return response
