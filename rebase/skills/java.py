
from .jvm_parser import JVMParser


def is_java(blob):
    return blob.name.endswith('.java')


def qualified_name(blob):
    return blob.path[:-5].replace('/', '.')


class Java(JVMParser):

    def __init__(self, host='parser', port=1111):
        super().__init__('Java')

    def context(self, commit):
        '''
        From 'commit', generate the list of importable packages in one long string.
        Java parser can then just 'find' the package name (of an ImportDeclaration node) in that string.
        The generated qualified names are longer than the real package names.
        That's ok because the remote Java parser will use 'find'.
        The simplicity comes from the fact that we do not have to parse every single java file for a 'package' statement,
        we just need to list java files path. It is also much faster.
        '''
        if not commit:
            return ''
        packages_ = ''
        q = [ commit.tree ]
        while q:
            tree = q.pop()
            packages_ += '|'+'|'.join( qualified_name(blob) for blob in tree.blobs if is_java(blob) )
            q.extend( tree.trees )
        return packages_


