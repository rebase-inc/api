from pprint import pprint
from unittest import TestCase

from ....skills.java import Java, qualified_name, packages
from ....skills.metrics import measure
from .git import Tree, Blob, Commit


class JavaTest(TestCase):

    def setUp(self):
        # build the parent commit
        Bar_java = Blob('Bar.java', 'a/Bar.java')
        Caca_js = Blob('Caca.js', 'a/b/Caca.js')
        parent_b = Tree('b', 'a/b', blobs=[Caca_js])
        parent_a = Tree('a', 'a', blobs=[Bar_java], trees=[parent_b])
        self.parent_commit = Commit(parent_a)

        # this commit just adds a file Foo.java
        self.Foo_java = Blob('Foo.java', 'a/b/Foo.java')
        b = Tree('b', 'a/b', blobs=[self.Foo_java, Caca_js])
        a = Tree('a', 'a', blobs=[Bar_java], trees=[b])
        self.commit = Commit(a)


    def test_qualified_name(self):
        Foo_java = Blob('Foo.java', 'a/b/Foo.java')
        self.assertEqual( qualified_name(Foo_java), 'a.b.Foo' )

    def test_packages(self):
        pkgs = packages(self.commit)
        self.assertNotEqual( pkgs.find('a.b.Foo'), -1 )
        self.assertNotEqual( pkgs.find('a.Bar'), -1 )
        self.assertEqual( pkgs.find('a.b.Caca'), -1 )

    def test_context(self):
        scanner = Java()
        context = scanner.context(self.commit, self.parent_commit)
        scanner.close()
        self.assertNotEqual( context[0].find('a.b.Foo'), -1 )
        self.assertNotEqual( context[0].find('a.Bar'), -1 )
        self.assertNotEqual( context[1].find('a.Bar'), -1 )
        self.assertEqual( context[1].find('a.b.Foo'), -1 )

    def test_scan_contents(self):
        # should be in functional tests really...
        foo_java = '''

            import a.b.Star;

            public class Bar {
                private Star zz = new Star();
            }
            
        '''
        scanner = Java()
        profile = scanner.scan_contents('foo.py', foo_java, 1234, ('a.b.Star', None))
        scanner.close()
        third_party_technologies = 0
        for technology in profile.keys():
            if technology.startswith('Java.__3rd_party__'):
                third_party_technologies += 1
        self.assertEqual( third_party_technologies, 0 )

    def test_scan_patch(self):
        Foo_java_code = '''
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
        scanner = Java()
        profile = scanner.scan_contents(
            self.Foo_java,
            Foo_java_code,
            1234,
            scanner.context(self.commit, self.parent_commit)
        )
        scanner.close()
        standard_library_technologies = 0
        third_party_technologies = 0
        for technology in profile.keys():
            if technology.startswith('Java.__std_library__'):
                standard_library_technologies += 1
            if technology.startswith('Java.__3rd_party__'):
                third_party_technologies += 1
        self.assertEqual( standard_library_technologies, 1 )
        self.assertEqual( third_party_technologies, 1 )
        IOException_key = 'Java.__std_library__.java.io.IOException'
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
        profile = scanner.scan_contents('foo.py', foo_java, 1234, ('', None))
        scanner.close()
        metrics = measure(profile)
        pprint(metrics)


