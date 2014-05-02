from django.core.management.base import BaseCommand
import timeit
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--fn',
            action='store',
            dest='test_fn',
            default=None,
            help='A specific function to test.'
        ),
    )
    def handle(self, *args, **options):

        def output_print(s, fn):
            print fn, round(min(s),2), round(max(s),2), round(sum(s)/len(s),2)
        test_fn = options['test_fn']

        fn = "hero_vitals_json"
        if test_fn == fn or test_fn is None:
            setup = "from heroes.json_data import {0}".format(fn)
            s = timeit.Timer("""hero_vitals_json(
                    [68],
                    ['strength']
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'hero_lineup_json'
        if test_fn == fn or test_fn is None:
            setup = "from heroes.json_data import {0}".format(fn)
            s = timeit.Timer("""hero_lineup_json([68],
                    'strength', 1)""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'hero_performance_chart_json'
        if test_fn == fn or test_fn is None:
            setup = "from heroes.json_data import {0}".format(fn)
            s = timeit.Timer("""hero_performance_chart_json(
                hero=53,
                player=85045426,
                game_modes=[1,2,3,4,5],
                x_var='duration',
                y_var='duration',
                group_var='skill_name',
                panel_var='is_win'
            )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'hero_progression_json'
        if test_fn == fn or test_fn is None:
            setup = "from heroes.json_data import {0}".format(fn)
            s = timeit.Timer("""hero_progression_json(
                hero=53,
                player=85045426,
                game_modes=[1,2,3,4,5],
                division='Skill'
            )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'hero_skillbuild_winrate_json'
        if test_fn == fn or test_fn is None:
            setup = "from heroes.json_data import {0}".format(fn)
            s = timeit.Timer("""hero_skillbuild_winrate_json(
                hero=53,
                player=85045426,
                game_modes=[1,2,3,4,5],
                levels=[5,10,15]
            )""", setup=setup).repeat(1, 1)
            output_print(s, fn)


        fn = 'update_player_winrate'
        if test_fn == fn or test_fn is None:
            setup = "from heroes.json_data import {0}".format(fn)
            s = timeit.Timer("""update_player_winrate(
                hero=53,
                game_modes=[1,2,3,4,5],
            )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        ##Matches
        fn = 'team_endgame_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""team_endgame_json(
                    players=[103611462, 85045426],
                    game_modes=[1,2,3,4,5],
                    x_var='duration',
                    y_var='kills',
                    panel_var='is_win',
                    group_var='none',
                    compressor='sum'
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'player_team_endgame_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""player_team_endgame_json(
                    players=[103611462, 85045426],
                    game_modes=[1,2,3,4,5],
                    x_var='duration',
                    y_var='K-D+.5*A',
                    panel_var='is_win',
                    group_var=None,
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'player_endgame_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""player_endgame_json(
                    players=[103611462, 85045426],
                    game_modes=[1,2,3,4,5],
                    x_var='duration',
                    y_var='K-D+.5*A',
                    panel_var=None,
                    group_var='is_win',
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'match_ability_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""match_ability_json(
                    match=528300921
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)


        fn = 'match_parameter_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""match_parameter_json(
                    match_id=528300921,
                    x_var='kills',
                    y_var='hero_damage',
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)


        fn = 'single_match_parameter_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""single_match_parameter_json(
                    match=528300921,
                    y_var='hero_damage',
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)


        fn = 'match_role_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""match_role_json(
                    match=528300921,
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)


        fn = 'match_list_json'
        if test_fn == fn or test_fn is None:
            setup = "from matches.json_data import {0}".format(fn)
            s = timeit.Timer("""match_list_json(
                    matches=[528300921,528019632],
                    player_list=[85045426]
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'player_winrate_json'
        if test_fn == fn or test_fn is None:
            setup = """from players.json_data import {0}
import datetime""".format(fn)
            s = timeit.Timer("""player_winrate_json(
                    player=85045426,
                    game_modes=None,
                    role_list=[],
                    min_date=datetime.date(2009, 1, 1),
                    max_date=None,
                    group_var='alignment',
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'player_hero_abilities_json'
        if test_fn == fn or test_fn is None:
            setup = "from players.json_data import {0}".format(fn)
            s = timeit.Timer("""player_hero_abilities_json(
                    player_1=103611462,
                    hero_1=5,
                    player_2=85045426,
                    hero_2=54,
                    game_modes=[1,2,3,4,5],
                    division=None
                    )""", setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'player_versus_winrate_json'
        if test_fn == fn or test_fn is None:
            setup = """from players.json_data import {0}
    import datetime""".format(fn)
            s = timeit.Timer("""player_versus_winrate_json(
                    player_1=103611462,
                    player_2=85045426,
                    game_modes=None,
                    min_date=datetime.date(2009, 1, 1),
                    max_date=None,
                    group_var='alignment',
                    plot_var='winrate',
                    )
            """, setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'player_hero_side_json'
        if test_fn == fn or test_fn is None:
            setup = """from players.json_data import {0}
    import datetime""".format(fn)
            s = timeit.Timer("""player_hero_side_json(
                    player=85045426,
                    game_modes=None,
                    min_date=datetime.date(2009, 1, 1),
                    max_date=None,
                    group_var='alignment',
                    plot_var='winrate',
            )
            """, setup=setup).repeat(1, 1)
            output_print(s, fn)

        fn = 'player_role_json'
        if test_fn == fn or test_fn is None:
            setup = """from players.json_data import {0}
    import datetime""".format(fn)
            s = timeit.Timer("""player_role_json(
                player_1=85045426,
                player_2=103611462,
                plot_var='performance',
            )
            """, setup=setup).repeat(1, 1)
            output_print(s, fn)
