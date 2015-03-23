from flask import jsonify, make_response, request
from flask.ext.login import current_user
from alveare.common.exceptions import ClientError
from alveare.common.database import DB
from sqlalchemy import or_

def get_collection(model, serializer, query_filter=None):
    query = model.query
    if query_filter is not None:
        query = query.filter(query_filter)
    all_instances = query.limit(100).all()
    return jsonify(**{model.__pluralname__: serializer.dump(all_instances, many=True).data})

def add_to_collection(model, deserializer, serializer):
    request_data = request.form or request.json
    new_instance = deserializer.load(request_data).data
    DB.session.add(new_instance)
    DB.session.commit()
    response = jsonify(**{model.__tablename__: serializer.dump(new_instance).data})
    response.status_code = 201
    return response

def get_resource(model, instance_id, serializer):
    instance = model.query.get(instance_id)
    if not instance:
        raise ClientError(404)
    return jsonify(**{model.__tablename__: serializer.dump(instance).data})

def update_resource(model, instance_id, update_deserializer, serializer):
    instance = model.query.get(instance_id)
    if not instance:
        raise ClientError(404)
    fields_to_update = update_deserializer.load(request.form or request.json).data
    for field, value in fields_to_update.items():
        if getattr(instance, field) != value:
            setattr(instance, field, value)
    DB.session.add(instance)
    DB.session.commit()
    return jsonify(**{model.__tablename__: serializer.dump(instance).data})

def delete_resource(model, instance_id):
    instance = model.query.get_or_404(instance_id)
    if not instance:
        raise ClientError(404)
    DB.session.delete(instance)
    DB.session.commit()

    response = jsonify(message = '{} succesfully deleted'.format(model.__tablename__))
    response.status_code = 200
    return response

def admin_required():
    def wrapper(rest_method):
        @wraps(rest_method)
        def admin_rest_method(*args, **kwargs):
            if not current_user.is_admin():
                return current_app.login_manager.unauthorized()
            return rest_method(*args, **kwargs)
        return admin_rest_method
    return wrapper

def query_string_values(query_string_name):
    values = [int(value) for value in request.args.get(query_string_name, '').split(',') if value]
    return values
