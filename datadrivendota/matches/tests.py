"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.test import TestCase
from datadrivendota.test_mixins import UrlTestMixin


# TESTS
class SimpleMatchUrlTest(UrlTestMixin, TestCase):
    fixtures = ['test_fixture.json']
    prefix = '/matches/'
    simple_urls = [
        '',
        'follow-matches/',
        'endgame/', 'team-endgame/',
        'own-team-endgame/',
        'ability-build/',
        'progression-list/',
    ]
    api_urls = [
        'api/endgame/?players=Na%60Vi.Dendi&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&x_var=duration&y_var=K-D%2B.5*A&panel_var=None&group_var=player&width=350&height=350',
        'api/role-scatter/?match=571286822&width=225&height=225&no_legend=true',
        'api/match-bar/?match=557410162&y_var=K-D%2B.5*A&width=375',
        'api/ability-build/?match=557410162&panel_var=side&width=225&height=225',
        'api/match-scatter/?match_id=557410162&x_var=gold_per_min&y_var=xp_per_min&width=225&height=225',
        # 'api/gettags/?term=aba',
        # 'api/getmatches/',
        'api/own-team-endgame/?players=Na%60Vi.Dendi&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&x_var=duration&y_var=kills&panel_var=is_win&group_var=is_win&compressor=sum',
        'api/same-team-endgame/?players=Na%60Vi.Dendi&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&x_var=duration&y_var=kills&panel_var=is_win&group_var=is_win&compressor=sum',
        # 'api/progression/',

    ]
