from unittest import TestCase
from alveare.common.utils import (
    pick_a_word,
    pick_a_first_name,
    pick_a_last_name,
    pick_an_organization_name,
)

class TestUtils(TestCase):

    def test_pick_a_word(self):
        for i in range(10):
            print(pick_a_word())
        word = pick_a_word(5, 7)
        self.assertGreaterEqual(len(word), 5)
        self.assertLessEqual(len(word), 7)

    def test_pick_a_first_name(self):
        print(pick_a_first_name())

    def test_pick_a_last_name(self):
        print(pick_a_last_name())

    def test_pick_an_organization_name(self):
        print(pick_an_organization_name())

