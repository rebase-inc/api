
def register_routes(api):
    from alveare.resources.user import UserCollection, UserResource
    api.add_resource(UserCollection, '/users', endpoint='users')
    api.add_resource(UserResource, '/users/<int:id>', endpoint='user')
