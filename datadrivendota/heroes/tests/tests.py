from django.test import TestCase


class TestBase(TestCase):

    def setUp(self):
        pass

    def test_add(self):
        self.assertEqual(2+2, 4)


class TestHeroes(TestCase):

    def setUp(self):
        pass

    def test_add(self):
        self.assertEqual(2+2, 4)
