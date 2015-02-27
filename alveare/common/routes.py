
def register_routes(api):
    from alveare.resources.user import UserCollection, UserResource
    api.add_resource(UserCollection, '/users', endpoint='users')
    api.add_resource(UserResource, '/users/<int:id>', endpoint='user')

    from alveare.resources.organization import OrganizationCollection, OrganizationResource
    api.add_resource(OrganizationCollection, '/organizations', endpoint='organizations')
    api.add_resource(OrganizationResource, '/organizations/<int:id>', endpoint='organization')

    from alveare.resources.manager import ManagerCollection, ManagerResource
    api.add_resource(ManagerCollection, '/managers', endpoint='managers')
    api.add_resource(ManagerResource, '/managers/<int:id>', endpoint='manager')
