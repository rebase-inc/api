
def register_routes(api):
    from alveare.resources.user import UserCollection
    api.add_resource(UserCollection, '/users', endpoint='users')
