def query_from_class_to_user(klass, path, user, id=None):
    query = klass.query
    if id:
        query = query.filter(klass.id==id)
    for node in path:
        query = query.join(node)
    return query.filter(path[-1].user == user)

