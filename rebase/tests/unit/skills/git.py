

def Blob(name, path, contents=None):
    return type('_Blob', (object,), { 'path': path, 'name': name, 'contents': contents})


def Tree(name, path, blobs=None, trees=None):
    return type('_Tree', (object,), {
        'name': name,
        'path': path,
        'blobs': blobs or list(),
        'trees': trees or list()
    })

def Commit(tree):
    return type('_Commit', (object,), {'tree': tree})


