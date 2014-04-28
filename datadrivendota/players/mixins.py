from .forms import (
    PlayerWinrateLevers,
    HeroAbilitiesForm,
    PlayerAdversarialForm,
    VersusWinrateForm,
    RoleForm,
)

from .json_data import (
    player_hero_side_json,
    player_winrate_json,
    player_hero_abilities_json,
    player_versus_winrate_json,
    player_role_json,
)


class WinrateMixin(object):
    form = PlayerWinrateLevers
    attrs = [
        'player',
        'game_modes',
        'min_date',
        'group_var',
    ]
    json_function = staticmethod(player_winrate_json)


class HeroAdversaryMixin(object):
    form = PlayerAdversarialForm
    attrs = [
        'player',
        'game_modes',
        'min_date',
        'max_date',
        'group_var',
        'plot_var',
    ]
    json_function = staticmethod(player_hero_side_json)


class HeroAbilitiesMixin(object):
    form = HeroAbilitiesForm
    attrs = [
        'player_1',
        'hero_1',
        'player_2',
        'hero_2',
        'game_modes',
        'division',
    ]
    json_function = staticmethod(player_hero_abilities_json)


class VersusWinrateMixin(object):
    form = VersusWinrateForm
    attrs = [
        'player_1',
        'player_2',
        'game_modes',
        'min_date',
        'max_date',
        'group_var',
        'plot_var',
    ]
    json_function = staticmethod(player_versus_winrate_json)


class RoleMixin(object):
    form = RoleForm
    attrs = [
        'player_1',
        'player_2',
        'plot_var',
    ]
    json_function = staticmethod(player_role_json)
