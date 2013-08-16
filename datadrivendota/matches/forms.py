from django import forms
from django.db.models import Q
from steamusers.models import SteamUser

users = SteamUser.objects.filter(Q(steam_id=66289584)| #Me
                                 Q(steam_id=68083913)| #Nath
                                 Q(steam_id=85045426)| #mig
                                 Q(steam_id=103611462) #meg
                                 )
user_list = [(user.steam_id, user.steam_id) for user in users]
user_list = [(66289584,'Ben: 66289584'),
             (68083913,'Nath: 68083913'),
             (85045426,'Mig: 85045426'),
             (103611462,'Meg: 103611462')]
parameters = ['duration','kills','deaths','assists','gold',
              'last_hits','denies','hero_damage','tower_damage','hero_healing',
              'level','is_win']
doubled_list = [(item, item) for item in parameters]

split_params = ['player','is_win','game_mode']
doubled_param_list = [(item,item) for item in split_params]

class EndgameSelect(forms.Form):
    players = forms.MultipleChoiceField(choices=user_list)
    x_var = forms.ChoiceField(choices=doubled_list)
    y_var = forms.ChoiceField(choices=doubled_list)
    split_var = forms.ChoiceField(choices=doubled_param_list)
    group_var = forms.ChoiceField(choices=doubled_param_list)
