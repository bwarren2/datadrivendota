from django import forms
from players.form_fields import SinglePlayerField
from .form_fields import MultiGameModeSelect



class EndgameSelect(forms.Form):

    SHARED_PARAMETERS = ['kills','deaths','assists','gold',
                  'last_hits','denies','hero_damage','tower_damage','hero_healing',
                  'level','K-D+.5*A']
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0,'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    SPLIT_PARAMS = ['player','is_win','game_mode']
    DOUBLED_PARAM_LIST = [(item,item) for item in SPLIT_PARAMS]

    players = SinglePlayerField(required=True)
    game_modes = MultiGameModeSelect(required=True)
    x_var = forms.ChoiceField(choices=X_LIST, required=True)
    y_var = forms.ChoiceField(choices=Y_LIST, required=True)
    split_var = forms.ChoiceField(choices=DOUBLED_PARAM_LIST, required=True)
    group_var = forms.ChoiceField(choices=DOUBLED_PARAM_LIST, required=True)

