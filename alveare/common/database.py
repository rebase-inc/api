#!/usr/bin/env python
from flask.ext.sqlalchemy import SQLAlchemy
DB = SQLAlchemy()

def get_or_make_object(model, data):
    if 'id' in data:
        instance = model.query.get(data.get('id'))
        if not instance:
            data['__name'] = model.__tablename__
            raise ValueError('No {__name} with id {id}'.format(**data))
        return instance
    return model(**data)

def update_object(model, data):
    if 'id' in data:
        instance = get_or_make_object(model, data)
        for key, value in data.items():
            if key == 'id': continue
            if getattr(instance, key) != value:
                setattr(instance, key, value)
        return instance
    else:
        data['__name'] = model.__tablename__
        raise ValueError('No {__name} id given!'.format(**data))
