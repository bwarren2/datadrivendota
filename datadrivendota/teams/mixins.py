from .forms import (
    TeamWinrateLevers
)


from .json_data import (
    team_winrate_json,
    team_pick_ban_json
)


class WinrateMixin(object):
    form = TeamWinrateLevers
    attrs = [
        'team',
        'min_date',
        'max_date',
        'group_var',
    ]
    json_function = staticmethod(team_winrate_json)


class PickBanMixin(object):
    form = TeamWinrateLevers
    attrs = [
        'team',
        'min_date',
        'max_date',
        'group_var',
    ]
    json_function = staticmethod(team_pick_ban_json)

