
# TODO remove this code and file once the refactoring of permissions is completed
def query_from_class_to_user(klass, path, user):
    query = klass.query
    for node in path:
        query = query.join(node)
    query = query.filter((path[-1].user if path else klass.user) == user)
    return query

