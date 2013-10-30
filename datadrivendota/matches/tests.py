"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

#MIXINS
class MatchValidityMixin(object):
    def setUp(self):
        self.valid_x_var = 'duration'
        self.invalid_x_var = 'blicketude'
        self.valid_y_var='kills'
        self.invalid_y_var='snufflupagus'
        self.valid_cat_var='is_win'
        self.invalid_cat_var='chumbliness'
        self.valid_game_modes=[1,2,3]
        self.invalid_game_modes=[-1,-2]
        super(MatchValidityMixin,self).setUp()

#TESTS
class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

