from .forms import (
    LeagueWinrateLevers
)

from .json_data import (
    league_winrate_json,
    league_pick_ban_json,
)


class WinrateMixin(object):
    form = LeagueWinrateLevers
    attrs = [
        'league',
        'min_date',
        'max_date',
        'group_var',
    ]
    json_function = staticmethod(league_winrate_json)


class PickBanMixin(object):
    form = LeagueWinrateLevers
    attrs = [
        'league',
        'min_date',
        'max_date',
        'group_var',
    ]
    json_function = staticmethod(league_pick_ban_json)
