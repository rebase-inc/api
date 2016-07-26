from io import BytesIO
from unittest import TestCase

from rebase.subprocess.json_subprocess import JsonReaderWriter


class RW(TestCase):

    def setUp(self):
        self.f = BytesIO()

    def cleanup(self):
        self.f.close()

    def test_a(self):
        jrw = JsonReaderWriter()
        o = {'a': 1, 'b': 2}
        jrw.write(self.f, o)
        self.f.seek(0)
        o_ = jrw.read(self.f)
        self.assertEqual(o, o_)


