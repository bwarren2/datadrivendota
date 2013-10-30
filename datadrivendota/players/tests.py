"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

###MIXINS
class PlayerValidityMixin(object):
    def setUp(self):
        self.valid_player = 1
        self.invalid_player = -1
        super(PlayerValidityMixin,self).setUp()

###TESTS
class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
