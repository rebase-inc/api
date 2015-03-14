
from flask.ext.restful import Resource
from flask import jsonify, make_response, request
from alveare.common.database import DB

def make_collection_and_resource_classes(
    Model,
    model,
    models,
    serializer,
    deserializer,
    update_deserializer
):
    class AlveareCollection(Resource):

        def get(self):
            things = Model.query.all()
            response = jsonify(**{ models: serializer.dump(things, many=True).data })
            return response

        def post(self):
            new_thing = deserializer.load(request.form or request.json).data

            DB.session.add(new_thing)
            DB.session.commit()

            response = jsonify(**{model: serializer.dump(new_thing).data})
            response.status_code = 201
            return response


    class AlveareResource(Resource):

        def get(self, id):
            thing = Model.query.get_or_404(id)
            return jsonify(**{model: serializer.dump(thing).data})

        def put(self, id):
            updated_thing = update_deserializer.load(request.form or request.json).data

            DB.session.add(updated_thing)
            DB.session.commit()

            response = jsonify(**{model: serializer.dump(updated_thing).data})
            response.status_code = 200
            return response

        def delete(self, id):
            DB.session.query(Model).filter_by(id=id).delete()
            DB.session.commit()

            response = jsonify(message = '{} succesfully deleted'.format(Model.__name__))
            response.status_code = 200
            return response
    return AlveareCollection, AlveareResource

def add_alveare_resource(
    api,
    Model,
    model,
    models,
    url_suffix,
    serializer,
    deserializer,
    update_deserializer
):
    '''
    Declares a new resource for the Model, and adds 2 paths: one for a collection,
    the other for a single resource.

    api is a Flask api object.
    Model is a SqlAlchemy Model class.
    model is a string that represents the singular name of the resource.
    models is a string that represents the plural name of the resource.
    url_suffix is a string that forms the suffix of the URI for a single resource.
    serializer, deserializer, update_serializer map to GET, POST, PUT respectively.

    TODO: this could be abstracted more using 2 maps of HTTP verbs (one for the collection, one for a single resource)
    '''

    ModelCollection, ModelResource = make_collection_and_resource_classes(
        Model,
        model,
        models,
        serializer,
        deserializer,
        update_deserializer
    )
    api.add_resource(ModelCollection, '/{}'.format(models), endpoint=models)
    api.add_resource(ModelResource, '/{}{}'.format(models, url_suffix), endpoint=model)
