from .forms import (
    EndgameSelect,
    TeamEndgameSelect,
    MatchAbilitySelect,
    MatchListSelect,
    MatchParameterSelect,
    SingleMatchParameterSelect,
    RoleSelect,
)
from .json_data import (
    player_endgame_json,
    team_endgame_json,
    match_ability_json,
    match_list_json,
    player_team_endgame_json,
    match_parameter_json,
    single_match_parameter_json,
    match_role_json
)


class EndgameMixin(object):
    form = EndgameSelect
    attrs = [
        'players',
        'game_modes',
        'x_var',
        'y_var',
        'panel_var',
        'group_var',
    ]
    json_function = staticmethod(player_endgame_json)


class OwnTeamEndgameMixin(object):
    form = EndgameSelect
    attrs = [
        'players',
        'game_modes',
        'x_var',
        'y_var',
        'panel_var',
        'group_var',
    ]
    json_function = staticmethod(player_team_endgame_json)


class SameTeamEndgameMixin(object):
    form = TeamEndgameSelect
    attrs = [
        'players',
        'game_modes',
        'x_var',
        'y_var',
        'panel_var',
        'group_var',
        'compressor',
    ]
    json_function = staticmethod(team_endgame_json)


class ProgressionListMixin(object):
    form = MatchListSelect
    attrs = [
        'match_list',
        'player_list',
    ]
    json_function = staticmethod(match_list_json)


class AbilityBuildMixin(object):
    form = MatchAbilitySelect
    attrs = [
        'match',
        'panel_var',
    ]
    json_function = staticmethod(match_ability_json)


class MatchParameterMixin(object):
    form = MatchParameterSelect
    attrs = [
        'match_id',
        'x_var',
        'y_var',
    ]
    json_function = staticmethod(match_parameter_json)


class SingleMatchParameterMixin(object):
    form = SingleMatchParameterSelect
    attrs = [
        'match',
        'y_var',
    ]
    json_function = staticmethod(single_match_parameter_json)


class RoleMixin(object):
    form = RoleSelect
    attrs = [
        'match',
    ]
    json_function = staticmethod(match_role_json)
