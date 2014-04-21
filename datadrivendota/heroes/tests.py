"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.core import urlresolvers
from .test_mixins import HeroValidityMixin
from heroes.urls import urlpatters as hero_urls
import unittest
# from django.test.client import Client
# from matches.tests import MatchValidityMixin


# TESTS
# R
# @todo: Consider using factoryboy for generating test objects. It's a cool
# library!
# --kit 2014-02-16
class HeroesUrlTest(HeroValidityMixin, TestCase):
    fixtures = ['datadrivendota/heroes/test_data.json']

    def setUp(self):
        User.objects.create_user(
            'temporary',
            'temporary@gmail.com',
            'temporary'
        )
        super(HeroesUrlTest, self).setUp()

    url_names = [p.name for p in hero_urls]
    vs = vars()

    def make_test_function(idx, url_name, url):
        def t(self):
            response = self.client.get(url)
            self.assertHttp200(response)
        t.__name__ = 'test_' + idx
        t.__doc__ = 'simple get test for ' + url_name
        return t

    for i, url_name in enumerate(url_names):
        i = str(i)
        try:
            url = urlresolvers.reverse(url_name, args=(), kwargs={})
            vs['test_' + i] = make_test_function(i, url_name, url)
        except urlresolvers.NoReverseMatch as e:
            vs['test_' + i] = unittest.skip(
                url_name + ' requires parameter(s) or view not found'
                )(lambda: 0)

    del url_names, vs, make_test_function,
