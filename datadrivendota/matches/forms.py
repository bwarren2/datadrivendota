from django import forms
from django.db.models import Q
from players.models import Player
from matches.models import GameMode

game_modes = GameMode.objects.all()
game_mode_choices = [(gm.steam_id, gm.description) for gm in game_modes]
users = Player.objects.filter(Q(steam_id=66289584)| #Me
                                 Q(steam_id=68083913)| #Nath
                                 Q(steam_id=85045426)| #mig
                                 Q(steam_id=103611462) #meg
                                 )
user_list = [(user.steam_id, user.steam_id) for user in users]
user_list = [(66289584,'Ben: 66289584'),
             (68083913,'Nath: 68083913'),
             (85045426,'Mig: 85045426'),
             (103611462,'Meg: 103611462')]
shared_parameters = ['kills','deaths','assists','gold',
              'last_hits','denies','hero_damage','tower_damage','hero_healing',
              'level','K-D+.5*A']
x_parameters = list(shared_parameters)
x_parameters.insert(0,'duration')

x_list = [(item, item) for item in x_parameters]
y_list = [(item, item) for item in shared_parameters]

split_params = ['player','is_win','game_mode']
doubled_param_list = [(item,item) for item in split_params]

class EndgameSelect(forms.Form):
    players = forms.MultipleChoiceField(choices=user_list, required=True)
    game_modes = forms.MultipleChoiceField(choices=game_mode_choices, required=True)
    x_var = forms.ChoiceField(choices=x_list, required=True)
    y_var = forms.ChoiceField(choices=y_list, required=True)
    split_var = forms.ChoiceField(choices=doubled_param_list, required=True)
    group_var = forms.ChoiceField(choices=doubled_param_list, required=True)
