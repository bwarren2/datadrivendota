from django.core.management.base import BaseCommand
import timeit


class Command(BaseCommand):

    def handle(self, *args, **options):

        def output_print(s, fn):
            print fn, round(min(s),2), round(max(s),2), round(sum(s)/len(s),2)

        fn = "hero_vitals_json"
        setup = "from heroes.json_data import {0}".format(fn)
        s = timeit.Timer("""hero_vitals_json(
                [68],
                ['strength']
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'hero_lineup_json'
        setup = "from heroes.json_data import {0}".format(fn)
        s = timeit.Timer("""hero_lineup_json([68],
                'strength', 1)""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'hero_performance_chart_json'
        setup = "from heroes.json_data import {0}".format(fn)
        s = timeit.Timer("""hero_performance_chart_json(
            hero=53,
            player=85045426,
            game_mode_list=[1,2,3,4,5],
            x_var='duration',
            y_var='duration',
            group_var='skill_name',
            split_var='is_win'
        )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'hero_progression_json'
        setup = "from heroes.json_data import {0}".format(fn)
        s = timeit.Timer("""hero_progression_json(
            hero=53,
            player=85045426,
            game_modes=[1,2,3,4,5],
            division='Skill'
        )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'hero_skillbuild_winrate_json'
        setup = "from heroes.json_data import {0}".format(fn)
        s = timeit.Timer("""hero_skillbuild_winrate_json(
            hero=53,
            player=85045426,
            game_modes=[1,2,3,4,5],
            levels=[5,10,15]
        )""", setup=setup).repeat(5, 1)
        output_print(s, fn)


        fn = 'update_player_winrate'
        setup = "from heroes.json_data import {0}".format(fn)
        s = timeit.Timer("""update_player_winrate(
            hero=53,
            game_modes=[1,2,3,4,5],
        )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        ##Matches
        fn = 'team_endgame_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""team_endgame_json(
                players=[103611462, 85045426],
                game_modes=[1,2,3,4,5],
                x_var='duration',
                y_var='kills',
                split_var='is_win',
                group_var='none',
                compressor='sum'
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'player_team_endgame_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""player_team_endgame_json(
                players=[103611462, 85045426],
                game_modes=[1,2,3,4,5],
                x_var='duration',
                y_var='K-D+.5*A',
                split_var='is_win',
                group_var='No Split',
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)


        fn = 'player_endgame_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""player_endgame_json(
                players=[103611462, 85045426],
                game_modes=[1,2,3,4,5],
                x_var='duration',
                y_var='K-D+.5*A',
                split_var='No Split',
                group_var='is_win',
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'match_ability_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""match_ability_json(
                match=528300921
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)


        fn = 'match_parameter_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""match_parameter_json(
                match_id=528300921,
                x_var='kills',
                y_var='hero_damage',
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)


        fn = 'single_match_parameter_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""single_match_parameter_json(
                match=528300921,
                y_var='hero_damage',
                title='hero_damage',
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)


        fn = 'match_role_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""match_role_json(
                match=528300921,
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)


        fn = 'match_list_json'
        setup = "from matches.json_data import {0}".format(fn)
        s = timeit.Timer("""match_list_json(
                match_list=[528300921,528019632],
                player_list=[85045426]
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'player_winrate_json'
        setup = """from players.json_data import {0}
import datetime""".format(fn)
        s = timeit.Timer("""player_winrate_json(
                player=85045426,
                game_modes=None,
                role_list=[],
                min_date=datetime.date(2009, 1, 1),
                max_date=None,
                group_var='alignment',
                )""", setup=setup).repeat(5, 1)

        output_print(s, fn)

        fn = 'player_hero_abilities_json'
        setup = "from players.json_data import {0}".format(fn)
        s = timeit.Timer("""player_hero_abilities_json(
                player_1=103611462,
                hero_1=5,
                player_2=85045426,
                hero_2=54,
                game_modes=[1,2,3,4,5],
                division=None
                )""", setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'player_versus_winrate_json'
        setup = """from players.json_data import {0}
import datetime""".format(fn)
        s = timeit.Timer("""player_versus_winrate_json(
                player_id_1=103611462,
                player_id_2=85045426,
                game_mode_list=None,
                min_date=datetime.date(2009, 1, 1),
                max_date=None,
                group_var='alignment',
                plot_var='winrate',
                )
        """, setup=setup).repeat(5, 1)
        output_print(s, fn)

        fn = 'player_hero_side_json'
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
        """, setup=setup).repeat(5, 1)
        output_print(s, fn)


        fn = 'player_role_json'
        setup = """from players.json_data import {0}
import datetime""".format(fn)
        s = timeit.Timer("""player_role_json(
            player_1=85045426,
            player_2=103611462,
            plot_var='performance',
        )
        """, setup=setup).repeat(5, 1)
        output_print(s, fn)

