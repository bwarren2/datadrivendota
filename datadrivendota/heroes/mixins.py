from .json_data import (
    hero_vitals_json,
    hero_lineup_json,
    hero_progression_json,
    hero_performance_chart_json,
    hero_skillbuild_winrate_json,
    update_player_winrate,
    hero_performance_lineup,
    hero_pick_rate_lineup,
)

from .forms import (
    HeroVitalsMultiSelect,
    HeroLineupMultiSelect,
    HeroPlayerPerformance,
    HeroProgressionForm,
    HeroBuildForm,
    UpdatePlayerWinrateForm,
    HeroPerformanceLineupForm,
    HeroPickRateForm,
)


class VitalsMixin(object):
    form = HeroVitalsMultiSelect
    attrs = [
        'heroes',
        'stats',
    ]
    json_function = staticmethod(hero_vitals_json)


class LineupMixin(object):
    form = HeroLineupMultiSelect
    attrs = [
        'heroes',
        'stat',
        'level',
    ]
    json_function = staticmethod(hero_lineup_json)


class HeroPerformanceMixin(object):
    form = HeroPlayerPerformance
    attrs = [
        'hero',
        'player',
        'game_modes',
        'x_var',
        'y_var',
        'group_var',
        'panel_var',
    ]
    json_function = staticmethod(hero_performance_chart_json)


class HeroSkillProgressionMixin(object):
    form = HeroProgressionForm
    attrs = [
        'hero',
        'player',
        'game_modes',
        'division',
    ]
    json_function = staticmethod(hero_progression_json)


class HeroBuildLevelMixin(object):
    form = HeroBuildForm
    attrs = [
        'hero',
        'player',
        'game_modes',
        'levels',
    ]
    json_function = staticmethod(hero_skillbuild_winrate_json)


class UpdatePlayerWinrateMixin(object):
    form = UpdatePlayerWinrateForm
    attrs = [
        'hero',
        'player',
        'game_modes',
        'levels',
    ]
    json_function = staticmethod(update_player_winrate)


class HeroPerformanceLineupMixin(object):
    form = HeroPerformanceLineupForm
    attrs = [
        'stat',
        'skill_level',
        'min_date',
        'max_date',
        'is_win',
        'heroes',
    ]
    json_function = staticmethod(hero_performance_lineup)


class HeroPickRateMixin(object):
    form = HeroPickRateForm
    attrs = [
        'var',
        'skill_level',
        'player',
        'heroes'
    ]
    json_function = staticmethod(hero_pick_rate_lineup)
