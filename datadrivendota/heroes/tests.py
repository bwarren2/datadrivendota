"""
"""
from django.test import TestCase
# from django.test.client import Client
# from matches.tests import MatchValidityMixin
from datadrivendota.test_mixins import UrlTestMixin

# TESTS
# @todo: Consider using factoryboy for generating test objects. It's a cool
# library!
# --kit 2014-02-16


class SimpleHeroUrlTest(UrlTestMixin, TestCase):
    fixtures = ['test_fixture.json']
    prefix = '/heroes/'
    simple_urls = [
        '',
        'vitals/',
        'lineups/',
        'performance/',
        'performance-lineup/',
        'skillbuild-winrate/',
        'skill-progression/',
        'Juggernaut/',
        'performance-lineup/',
        'ability/juggernaut_healing_ward/',
    ]

    api_urls = [
        'api/vitals_chart/?heroes=Juggernaut&stats=strength',
        'api/lineup_chart/?heroes=Juggernaut&stat=strength&level=1',
        'api/skill_progression_chart/?hero=Juggernaut&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&division=Skill',
        'api/build_level_chart/?hero=Juggernaut&player=Na%60Vi.Dendi&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&levels=5&width=275&height=275',
        'api/hero_performance_chart/?hero=Juggernaut&player=&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&division=Skill&x_var=duration&y_var=tower_damage&group_var=skill_name&panel_var=is_win&width=275&height=275',
        'api/update_player_winrate/?hero=Juggernaut&game_modes=1&game_modes=2&game_modes=3&game_modes=4&game_modes=5&width=300&height=300',
        'api/hero_performance_lineup/?heroes=Juggernaut&stat=kills&skill_level=1&min_date=2009-04-01&max_date=2014-05-06&is_win=win',
        # 'api/getheroes?term=ju',
    ]
