from django import forms
from players.form_fields import MultiPlayerField
from .form_fields import (
    MultiGameModeSelect,
    MultiMatchSelect,
    SingleMatchSelect,
    )
from heroes.form_fields import SingleHeroSelect
from datadrivendota.form_fields import OutcomeField


class EndgameSelect(forms.Form):

    SHARED_PARAMETERS = [
        'kills',
        'deaths',
        'assists',
        'gold_total',
        'xp_total',
        'last_hits',
        'denies',
        'hero_damage',
        'tower_damage',
        'hero_healing',
        'level',
        'K-D+.5*A',
        'first_blood_time'
    ]
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0, 'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    SPLIT_PARAMS = ['player', 'is_win', 'game_mode', 'None']
    DOUBLED_PARAM_LIST = [(item, item) for item in SPLIT_PARAMS]

    players = MultiPlayerField(
        required=True,
        help_text='Pick one player.  Use the autocomplete.'
    )
    game_modes = MultiGameModeSelect(
        required=True,
        help_text='Which game modes would you like to sample?'
    )
    x_var = forms.ChoiceField(
        choices=X_LIST,
        required=True,
        help_text='What goes on the x axis?'
    )
    y_var = forms.ChoiceField(
        choices=Y_LIST,
        required=True,
        help_text='What goes on the y axis?'
    )
    panel_var = forms.ChoiceField(
        choices=DOUBLED_PARAM_LIST,
        required=True,
        help_text='Which variable splits data between panels?',
        initial='is_win'
    )
    group_var = forms.ChoiceField(
        choices=DOUBLED_PARAM_LIST,
        required=True,
        help_text='Which variable colors data within a panel?',
        initial='player'
    )


class TeamEndgameSelect(forms.Form):

    SHARED_PARAMETERS = [
        'kills',
        'deaths',
        'assists',
        'gold_total',
        'xp_total',
        'last_hits',
        'denies',
        'hero_damage',
        'tower_damage',
        'hero_healing',
        'level',
        'K-D+.5*A'
    ]
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0, 'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    SPLIT_PARAMS = ['is_win', 'game_mode', 'none', 'player']
    DOUBLED_PARAM_LIST = [(item, item) for item in SPLIT_PARAMS]
    COMPRESSOR_LIST = [(item, item) for item in ['sum', 'avg']]

    players = MultiPlayerField(
        required=True,
        help_text='Pick one player.  Use the autocomplete.'
    )
    game_modes = MultiGameModeSelect(
        required=True,
        help_text='Which game modes would you like to sample?'
    )
    x_var = forms.ChoiceField(
        choices=X_LIST,
        required=True,
        help_text='What goes on the x axis?'
    )
    y_var = forms.ChoiceField(
        choices=Y_LIST,
        required=True,
        help_text='What goes on the y axis?'
    )
    panel_var = forms.ChoiceField(
        choices=DOUBLED_PARAM_LIST,
        required=True,
        help_text='Which variable splits data between panels?',
        initial='is_win'
    )
    group_var = forms.ChoiceField(
        choices=DOUBLED_PARAM_LIST,
        required=True,
        help_text='Which variable colors data within a panel?',
        initial='is_win'
    )
    compressor = forms.ChoiceField(
        choices=COMPRESSOR_LIST,
        required=True,
        help_text="It's just a factor of 5",
        initial='sum'
    )


class MatchAbilitySelect(forms.Form):
    SPLIT_PARAMS = ['side', 'hero', 'None']
    DOUBLED_PARAM_LIST = [(item, item) for item in SPLIT_PARAMS]
    match = forms.IntegerField()
    panel_var = forms.ChoiceField(DOUBLED_PARAM_LIST)


class MatchListSelect(forms.Form):
    matches = MultiMatchSelect(
        required=True,
        help_text='Pick one or more matches by ID'
    )
    players = MultiPlayerField(
        required=True,
        help_text='Pick one or more players by name'
    )


class MatchParameterSelect(forms.Form):
    match_id = SingleMatchSelect(
        required=True,
        help_text='Pick one match by ID'
    )
    SHARED_PARAMETERS = [
        'kills',
        'deaths',
        'assists',
        'gold_total',
        'gold_per_min',
        'xp_total',
        'xp_per_min',
        'last_hits',
        'denies',
        'hero_damage',
        'tower_damage',
        'hero_healing',
        'level',
        'K-D+.5*A'
    ]
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0, 'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    x_var = forms.ChoiceField(
        choices=X_LIST,
        required=True,
        help_text='What goes on the x axis?'
    )
    y_var = forms.ChoiceField(
        choices=Y_LIST,
        required=True,
        help_text='What goes on the y axis?'
    )


class SingleMatchParameterSelect(forms.Form):
    match = SingleMatchSelect(
        required=True,
        help_text='Pick one match by ID'
    )
    SHARED_PARAMETERS = [
        'kills',
        'deaths',
        'assists',
        'gold_total',
        'gold_per_min',
        'xp_total',
        'xp_per_min',
        'last_hits',
        'denies',
        'hero_damage',
        'tower_damage',
        'hero_healing',
        'level',
        'K-D+.5*A'
    ]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    y_var = forms.ChoiceField(
        choices=Y_LIST,
        required=True,
        help_text='What goes on the y axis?'
    )


class RoleSelect(forms.Form):
    match = SingleMatchSelect(
        required=True,
        help_text='Pick one match by ID'
    )


class ContextSelect(forms.Form):
    hero = SingleHeroSelect(
        required=True,
        help_text='Pick one hero'
    )
    outcome = OutcomeField(
        required=True,
        help_text='What outcome would you like to compare against?')
    matches = MultiMatchSelect(
        required=False,
        help_text='Pick one or more matches'
    )


class MatchSetSelect(forms.Form):
    hero = SingleHeroSelect(
        required=True,
        help_text='Pick one hero'
    )
    match_set_1 = MultiMatchSelect(
        required=True,
        help_text='Pick one or more matches'
    )
    match_set_2 = MultiMatchSelect(
        required=False,
        help_text='Pick one or more matches'
    )
    match_set_3 = MultiMatchSelect(
        required=False,
        help_text='Pick one or more matches'
    )
