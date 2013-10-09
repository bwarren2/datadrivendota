from django import forms
from heroes.models import HeroDossier
from matches.models import GameMode

heroes = HeroDossier.objects.all().order_by('hero__name')
hero_list = [(dossier.hero.name, dossier.hero.name) for dossier in heroes]

vital_stat_pool = ['strength', 'intelligence', 'agility', 'modified_armor', 'effective_hp',
               'hp', 'mana']
vital_stats = [(item, item.replace("_"," ").title()) for item in vital_stat_pool]
lineup_stat_pool = vital_stat_pool
lineup_stat_pool.extend(['day_vision','night_vision','atk_point',
    'atk_backswing','turn_rate','legs','movespeed','projectile_speed',
    'range','base_atk_time'])
lineup_stats = [(item, item.replace("_"," ").title()) for item in lineup_stat_pool]



class HeroVitalsMultiSelect(forms.Form):

#    heroes = HeroMultiSelect(required=True)
    heroes = forms.CharField(required=True)
    heroes.widget=forms.TextInput(attrs={'class': 'hero-tags',})
    stats = forms.MultipleChoiceField(choices=vital_stats, required=True)
    unlinked_scales = forms.BooleanField(required=False)

class HeroLineupMultiSelect(forms.Form):
    heroes = forms.CharField(required=True)
    heroes.widget=forms.TextInput(attrs={'class': 'hero-tags',})
    stats = forms.ChoiceField(choices=lineup_stats, required=True)
    level = forms.ChoiceField(choices=[(i,i) for i in range(1,26)], required=True)


game_modes = GameMode.objects.all()
game_mode_choices = [(gm.steam_id, gm.description) for gm in game_modes]


shared_parameters = ['kills','deaths','assists','gold',
              'last_hits','denies','hero_damage','tower_damage','hero_healing',
              'level','K-D+.5*A']
x_parameters = list(shared_parameters)
x_parameters.insert(0,'duration')

x_list = [(item, item) for item in x_parameters]
y_list = [(item, item) for item in shared_parameters]

split_params = ['is_win','game_mode','skill_level']
doubled_param_list = [(item,item) for item in split_params]

class HeroPlayerPerformance(forms.Form):

    hero = forms.CharField(required=True)
    hero.widget=forms.TextInput(attrs={'class': 'hero-tags',})
    player = forms.CharField(required=False)
    player.widget=forms.TextInput(attrs={'class': 'player-tags',})
    game_modes = forms.MultipleChoiceField(choices=game_mode_choices, required=True)
    x_var = forms.ChoiceField(choices=x_list, required=True)
    y_var = forms.ChoiceField(choices=y_list, required=True)
    split_var = forms.ChoiceField(choices=doubled_param_list, required=True)
    group_var = forms.ChoiceField(choices=doubled_param_list, required=True)
