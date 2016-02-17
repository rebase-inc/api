
from flask.ext.sqlalchemy import SQLAlchemy

from rebase.common.exceptions import (
    AsContractorPathUndefined,
    AsManagerPathUndefined,
    AsOwnerPathUndefined,
    BadDataError,
    NotFoundError,
)


DB = SQLAlchemy()


class PermissionMixin(object):
    '''
    as_XXX_path are query paths that go from a queried model all the way up the role
    of the user doing the query.
    Therefore these paths must be either empty list (if the model queried is itself a role) or
    a non-empty list whose last element is the role type)
    '''
    as_contractor_path = None
    as_manager_path = None
    as_owner_path = None
    filter_based_on_current_role = True

    def allowed_to_be_created_by(self, user):
        msg = 'allowed_to_be_created_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_modified_by(self, user):
        msg = 'allowed_to_be_modified_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_deleted_by(self, user):
        msg = 'allowed_to_be_deleted_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_viewed_by(self, user):
        msg = 'allowed_to_be_viewed_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    @classmethod
    def query_from_class_to_user(klass, path, user):
        query = klass.query
        for node in path:
            query = query.join(node)
        role_model = path[-1] if path else klass
        if klass.filter_based_on_current_role:
            query = query.filter(role_model.id == user.current_role.id)
        else:
            query = query.filter(role_model.user == user)
        return query

    @classmethod
    def as_owner(cls, user):
        if cls.as_owner_path == None:
            raise AsOwnerPathUndefined(cls)
        return cls.query_from_class_to_user(cls.as_owner_path, user)

    @classmethod
    def as_contractor(cls, user):
        if cls.as_contractor_path == None:
            raise AsContractorPathUndefined(cls)
        return cls.query_from_class_to_user(cls.as_contractor_path, user)

    @classmethod
    def as_manager(cls, user):
        if cls.as_manager_path == None:
            raise AsManagerPathUndefined(cls)
        return cls.query_from_class_to_user(cls.as_manager_path, user)

    @classmethod
    def role_to_query_fn(cls, user):
        if user.current_role.type == 'manager':
            return cls.as_manager
        elif user.current_role.type == 'owner':
            return cls.as_owner
        elif user.current_role.type == 'contractor':
            return cls.as_contractor
        else:
            raise UnknownRole(user.current_role)

    @classmethod
    def query_by_user(cls, user):
        if user.is_admin():
            return cls.query
        return cls.role_to_query_fn(user)(user)

    @classmethod
    def found(cls, self, user):
        '''
        Returns True is 'user' can retrieve 'self' via one of the permitted paths (i.e. as_owner_path, as_contractor_path or as_manager_path).
        The permission path used is the one for the current_role of the 'user'.
        If 'user' is an admin, found always returns True.
        '''
        if user.admin:
            return True
        return self in self.query_by_user(user)

    @classmethod
    def setup_queries(cls, _):
        msg = 'setup_queries is not implemented for {}'
        #raise NotImplemented(msg.format(cls.__name__))
        #print(msg.format(cls.__name__))
    
    def __cache_repr__(self):
        return self.__mapper__.identity_key_from_instance(self)

    def __hash__(self):
        return hash(str(self.__cache_repr__()))


