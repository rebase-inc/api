#!/usr/bin/env python
from flask.ext.sqlalchemy import SQLAlchemy
DB = SQLAlchemy()

def get_or_make_object(model, data, id_fields=None):
    id_fields = id_fields or ['id']
    instance_id = tuple(data.get(id_field) for id_field in id_fields)
    if all(instance_id):
        instance = model.query.get(instance_id)
        if not instance:
            data['__name'] = model.__tablename__
            raise ValueError('No {__name} with id {id}'.format(**data))
        return instance
    return model(**data)
