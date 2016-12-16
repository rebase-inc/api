from bisect import bisect_left
from copy import copy
from functools import partial
from pprint import pprint
from unittest import TestCase

from rebase.datetime import utcnow_timestamp, DAY_SECONDS
from rebase.skills.aws_keys import profile_key, level_key
from rebase.skills.tech_profile import TechProfile
from rebase.skills.tech_profile_view import TechProfileView
from rebase.skills.metrics import measure
from rebase.skills.population import update_rankings as _update_rankings, get_rankings as _get_rankings


def add(prof_a, prof_b):
    for t, e in prof_b.items():
        prof_a[t] = copy(e)

def _wait_till_exists(): pass


class TP(TestCase):

    def setUp(self):
        now = utcnow_timestamp()
        day_1 = now - 365*DAY_SECONDS
        day_2 = now - 180*DAY_SECONDS
        day_3 = now - 14*DAY_SECONDS
        day_4 = now - DAY_SECONDS
        self.prof_1 = TechProfile()
        self.prof_1.add('Foo.0.bar', day_1, 1)
        self.prof_1.add('Foo.0.bar.mama', day_1, 4)
        self.prof_1.add('Foo.1.yo.mama', day_2, 1)
        self.prof_1.add('Foo.1.yo.mama', day_2, 1)

        self.prof_2= TechProfile()
        self.prof_2.add('Bar.2.yo', day_1, 5)
        self.prof_2.add('Bar.2.yo.mama', day_2, 1)
        self.prof_2.add('Bar.2.bar.mama', day_1, 9)

        self.prof_3 = TechProfile()
        add(self.prof_3, self.prof_1)
        add(self.prof_3, self.prof_2)

        self.prof_4 = TechProfile()
        add(self.prof_4, self.prof_1)
        self.prof_4.add('Foo.1.yo.mama', day_4, 1)

    def test_a(self):
        v1 = TechProfileView(self.prof_1)
        v2 = TechProfileView(self.prof_2)
        v3 = TechProfileView(self.prof_3)
        self.assertEqual(v1.breadth, 3)
        self.assertEqual(v2.breadth, 3)
        self.assertEqual(v1.depth, 7)
        self.assertEqual(v2.depth, 15)
        self.assertEqual(v3.breadth, 6)
        self.assertEqual(v3.depth, 22)
        self.assertGreater(v3.freshness, 0.0)
        metrics = measure(self.prof_3)
        print(metrics)

    def test_b(self):
        v1 = TechProfileView(self.prof_1)
        v3 = TechProfileView(self.prof_3)
        v4 = TechProfileView(self.prof_4)
        self.assertGreater(v3.breadth, v1.breadth)
        self.assertGreater(v3.depth, v1.depth)
        self.assertGreater(v3.experience, v1.experience)
        self.assertGreater(v4.freshness, v1.freshness)
        self.assertGreater(v4.experience, v1.experience)

    def test_ranking(self):
        s3 = dict()
        _exists = lambda key: s3.__contains__(key)
        update_rankings = partial(
            _update_rankings,
            consistent_get=lambda bucket, key, etag: s3.get(key),
            get=s3.get,
            put=s3.__setitem__,
            exists=_exists,
            wait_till_exists=_wait_till_exists,
            write_to_db=False,
        )
        get_rankings = partial(
            _get_rankings,
            get=s3.get,
            exists=_exists
        )

        user_1 = 'user_1'
        profile_1_key = profile_key(user_1)
        metrics_1 = measure(self.prof_1)
        saved_profile_1 = {
            'metrics': metrics_1
        }
        s3[profile_1_key] = saved_profile_1
        update_rankings(user_1, ('some_bucket', profile_1_key, 'some_etag'))
        _overall_key = level_key('_overall')
        self.assertIn(_overall_key, s3)
        self.assertEqual(s3[_overall_key], [metrics_1['_overall']])
        Foo_key = level_key('Foo')
        self.assertIn(Foo_key, s3)
        self.assertEqual(s3[Foo_key], [metrics_1['Foo']])
        print()
        pprint(s3)

        metrics_2 = measure(self.prof_2)
        user_2 = 'user_2'
        profile_2_key = profile_key(user_2)
        saved_profile_2 = {
            'metrics': metrics_2
        }
        s3[profile_2_key] = saved_profile_2
        update_rankings(user_2, ('some_bucket', profile_2_key, 'some_etag'))
        Bar_key = level_key('Bar')
        self.assertIn(Bar_key, s3)
        print()
        pprint(s3)

        gt = metrics_1['_overall'] < metrics_2['_overall']
        i1 = bisect_left(s3[_overall_key], metrics_1['_overall'])
        i2 = bisect_left(s3[_overall_key], metrics_2['_overall'])
        self.assertEqual(gt, i1 < i2)

        print()
        pprint(get_rankings(user_1))
        print()
        pprint(get_rankings(user_2))


