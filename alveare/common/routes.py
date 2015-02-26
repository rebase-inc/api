
def register_routes(api):
    from alveare.resources.user import UserCollection
    api.add_resource(UserCollection, '/users', endpoint='users')

    from alveare.resources.organization import OrganizationCollection
    api.add_resource(OrganizationCollection, '/organizations', endpoint='organizations')
