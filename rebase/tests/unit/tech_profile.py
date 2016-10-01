from unittest import TestCase

from rebase.skills.tech_profile import TechProfile
from rebase.skills.tech_profile_view import TechProfileView
from rebase.skills.metrics import measure


class TP(TestCase):

    def setUp(self):
        self.prof_1 = TechProfile()
        self.prof_1.add('Foo.bar', 123, 1)
        self.prof_1.add('Foo.bar.mama', 120, 4)
        self.prof_1.add('Foo.yo.mama', 123, 2)

        self.prof_2= TechProfile()
        self.prof_2.add('Bar.yo', 113, 5)
        self.prof_2.add('Bar.bar.mama', 127, 9)
        self.prof_2.add('Bar.yo.mama', 123, 1)

        self.prof_3 = TechProfile()
        self.prof_3.update(self.prof_1)
        self.prof_3.update(self.prof_2)

    def test_a(self):
        view = TechProfileView(self.prof_3)
        self.assertEqual(view.breadth, 6)
        self.assertEqual(view.depth, 22)
        self.assertGreater(view.freshness, 0.0)
        metrics = measure(self.prof_3)
        print(metrics)

    def test_b(self):
        v1 = TechProfileView(self.prof_1)
        v3 = TechProfileView(self.prof_3)
        self.assertGreater(v3.experience, v1.experience)


