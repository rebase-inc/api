
# TODO remove this code and file once the refactoring of permissions is completed
def query_from_class_to_user(klass, path, user):
    query = klass.query
    for node in path:
        query = query.join(node)
    query = query.filter((path[-1].user if path else klass.user) == user)
    return query


def query_by_user_or_id(cls, query_fn, filter_by_id, user, instance=None):
    if user.admin:
        query = cls.query
    else:
        query = query_fn(user)
    if instance:
        query = instance.filter_by_id(query)
    return query
