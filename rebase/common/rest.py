from flask import jsonify, request
from flask.ext.login import current_user, current_app
from rebase.common.exceptions import NotFoundError
from rebase.common.database import DB

def get_collection(model, serializer):
    query = model.query_by_user(current_user)
    all_instances = query.limit(100).all()
    serializer.context = dict(current_user = current_user)
    return jsonify(**{model.__pluralname__: serializer.dump(all_instances, many=True).data})

def add_to_collection(model, deserializer, serializer):
    new_instance = deserializer.load(request.form or request.json).data
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

def update_resource(model, instance_id, update_deserializer, serializer):
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
    return jsonify(**{model.__tablename__: serializer.dump(instance).data})

def delete_resource(model, instance_id):
    instance = model.query.get(instance_id)
    if not instance:
        raise NotFoundError(model.__tablename__, instance_id)
    if not instance.allowed_to_be_deleted_by(current_user):
        return current_app.login_manager.unauthorized()
    DB.session.delete(instance)
    DB.session.commit()

    response = jsonify(message = '{} succesfully deleted'.format(model.__tablename__))
    response.status_code = 200
    return response

def query_string_values(query_string_name):
    values = [int(value) for value in request.args.get(query_string_name, '').split(',') if value]
    return values
