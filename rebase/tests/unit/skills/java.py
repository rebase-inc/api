from pprint import pprint
from unittest import TestCase

from ....skills.java import Java, qualified_name
from ....skills.metrics import measure
from .git import Tree, Blob, Commit


class JavaTest(TestCase):

    def setUp(self):
        # build the parent commit
        Bar_java = Blob('Bar.java', 'a/Bar.java')
        self.Foo_java = Blob('Foo.java', 'a/b/Foo.java')
        Caca_js = Blob('Caca.js', 'a/b/Caca.js')
        parent_b = Tree('b', 'a/b', blobs=[self.Foo_java, Caca_js])
        parent_a = Tree('a', 'a', blobs=[Bar_java], trees=[parent_b])
        self.parent_commit = Commit(parent_a)

        # this commit modifies Foo.java
        self.Foo_java_2 = Blob('Foo.java', 'a/b/Foo.java')
        b = Tree('b', 'a/b', blobs=[self.Foo_java_2, Caca_js])
        a = Tree('a', 'a', blobs=[Bar_java], trees=[b])
        self.commit = Commit(a)


    def test_qualified_name(self):
        Foo_java = Blob('Foo.java', 'a/b/Foo.java')
        self.assertEqual( qualified_name(Foo_java), 'a.b.Foo' )

    def test_context(self):
        scanner = Java()
        context = scanner.context(self.commit)
        scanner.close()
        self.assertNotEqual( context.find('a.b.Foo'), -1 )
        self.assertNotEqual( context.find('a.Bar'), -1 )

    def test_scan_contents(self):
        # should be in functional tests really...
        foo_java = '''

            import a.b.Star;

            public class Bar {
                private Star zz = new Star();
            }
            
        '''
        scanner = Java()
        profile = scanner.scan_contents('foo.py', foo_java, 1234, self.commit)
        scanner.close()
        third_party_technologies = 0
        for technology in profile.keys():
            if technology.startswith('Java.2'):
                third_party_technologies += 1
        self.assertEqual( third_party_technologies, 1 )

    def test_scan_diff(self):
        code = '''
            // Standard Library
            import java.io.IOException;

            // 3rd-party Library
            import com.github.javaparser.ast.Node;

            // Private library
            import a.b.Foo;

            public class Bar {
                private Foo zz = new Foo();

                public Bar() {
                    Node node = new Node();
                }

                public void RaiseIOException() throws IOException {
                    IOException my_exception = new IOException("I pity the fool!");
                    throw my_exception;
                }

                public void RaiseIOExceptionNoLocalVar() throws IOException {
                    throw new IOException("Yo mama so fat she's a registered fracker");
                }
            }
            
        '''
        parent_code = '' # let's assume the initial version of Foo_java was empty 
        scanner = Java()
        profile = scanner.scan_diff(
            self.Foo_java.name,
            code,
            self.commit,
            parent_code,
            self.parent_commit,
            1234
        )
        scanner.close()
        standard_library_technologies = 0
        third_party_technologies = 0
        for technology in profile.keys():
            if technology.startswith('Java.1'):
                standard_library_technologies += 1
            if technology.startswith('Java.2'):
                third_party_technologies += 1
        self.assertEqual( standard_library_technologies, 1 )
        self.assertEqual( third_party_technologies, 1 )
        IOException_key = 'Java.1.java.io.IOException'
        self.assertIn( IOException_key, profile )
        IOException = profile[IOException_key]
        self.assertEqual( IOException.total_reps, 4 )

    def test_metrics(self):
        # should be in functional tests really...
        foo_java = '''

            import a.b.Star;
            import a.b.c.d.e.Zob;

            public class Bar {
                private Star zz = new Star();
                private Zob zob = new Zob();
            }
            
        '''
        scanner = Java()
        profile = scanner.scan_contents('foo.java', foo_java, 1234, self.commit)
        scanner.close()
        metrics = measure(profile)
        self.assertIn('Java.3rd-party.a.b.c', metrics)


