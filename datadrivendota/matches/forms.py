from django import forms
from players.form_fields import MultiPlayerField
from .form_fields import MultiGameModeSelect



class EndgameSelect(forms.Form):

    SHARED_PARAMETERS = ['kills','deaths','assists','gold_total',
                  'last_hits','denies','hero_damage','tower_damage','hero_healing',
                  'level','K-D+.5*A','first_blood_time']
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0,'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    SPLIT_PARAMS = ['player','is_win','game_mode']
    DOUBLED_PARAM_LIST = [(item,item) for item in SPLIT_PARAMS]

    players = MultiPlayerField(required=True, help_text='Pick one player.  Use the autocomplete.')
    game_modes = MultiGameModeSelect(required=True, help_text='Which game modes would you like to sample?')
    x_var = forms.ChoiceField(choices=X_LIST, required=True, help_text='What goes on the x axis?')
    y_var = forms.ChoiceField(choices=Y_LIST, required=True, help_text='What goes on the y axis?')
    split_var = forms.ChoiceField(choices=DOUBLED_PARAM_LIST, required=True,
        help_text='Which variable splits data between panels?',
        initial='is_win')
    group_var = forms.ChoiceField(choices=DOUBLED_PARAM_LIST, required=True,
        help_text='Which variable colors data within a panel?',
        initial='player')

class TeamEndgameSelect(forms.Form):

    SHARED_PARAMETERS = ['kills','deaths','assists','gold_total',
                  'last_hits','denies','hero_damage','tower_damage','hero_healing',
                  'level','K-D+.5*A']
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0,'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    SPLIT_PARAMS = ['is_win','game_mode','none']
    DOUBLED_PARAM_LIST = [(item,item) for item in SPLIT_PARAMS]
    COMPRESSOR_LIST = [(item,item) for item in ['sum','avg']]

    players = MultiPlayerField(required=True, help_text='Pick one player.  Use the autocomplete.')
    game_modes = MultiGameModeSelect(required=True, help_text='Which game modes would you like to sample?')
    x_var = forms.ChoiceField(choices=X_LIST, required=True, help_text='What goes on the x axis?')
    y_var = forms.ChoiceField(choices=Y_LIST, required=True, help_text='What goes on the y axis?')
    split_var = forms.ChoiceField(choices=DOUBLED_PARAM_LIST, required=True,
        help_text='Which variable splits data between panels?',
        initial='is_win')
    group_var = forms.ChoiceField(choices=DOUBLED_PARAM_LIST, required=True,
        help_text='Which variable colors data within a panel?',
        initial='is_win')
    compressor = forms.ChoiceField(choices=COMPRESSOR_LIST, required=True,
        help_text="It's just a factor of 5",
        initial='sum')

class MatchAbilitySelect(forms.Form):
    SPLIT_PARAMS = ['side','hero','No Split']
    DOUBLED_PARAM_LIST = [(item,item) for item in SPLIT_PARAMS]
    match = forms.IntegerField()
    split_var = forms.ChoiceField(DOUBLED_PARAM_LIST)
