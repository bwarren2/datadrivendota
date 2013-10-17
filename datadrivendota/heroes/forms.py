from django import forms
from django.forms import ValidationError
from matches.form_fields import MultiGameModeSelect
from players.form_fields import SinglePlayerField
from .form_fields import MultiHeroSelect, SingleHeroSelect




class HeroVitalsMultiSelect(forms.Form):
    VITAL_STAT_POOL = ['strength', 'intelligence', 'agility', 'modified_armor', 'effective_hp',
                   'hp', 'mana']
    VITAL_STATS = [(item, item.replace("_"," ").title()) for item in VITAL_STAT_POOL]

    heroes = MultiHeroSelect(required=True)
    stats = forms.MultipleChoiceField(choices=VITAL_STATS, required=True)
    unlinked_scales = forms.BooleanField(required=False)


class HeroLineupMultiSelect(forms.Form):

    VITAL_STAT_POOL = ['strength', 'intelligence', 'agility', 'modified_armor', 'effective_hp',
                   'hp', 'mana','day_vision','night_vision','atk_point',
        'atk_backswing','turn_rate','legs','movespeed','projectile_speed',
        'range','base_atk_time']

    LINEUP_STATS = [(item, item.replace("_"," ").title()) for item in VITAL_STAT_POOL]
    heroes = MultiHeroSelect(required=True)
    stats = forms.ChoiceField(choices=LINEUP_STATS, required=True)
    level = forms.ChoiceField(choices=[(i,i) for i in range(1,26)], required=True)


    def clean_level(self):
        lvl = self.cleaned_data['level']
        try:
            int_lvl = int(lvl)
        except TypeError:
            raise ValidationError("%s could not be turned into an int"%lvl)
        return int_lvl

class HeroPlayerPerformance(forms.Form):

    SHARED_PARAMETERS = ['kills','deaths','assists','gold',
                  'last_hits','denies','hero_damage','tower_damage','hero_healing',
                  'level','K-D+.5*A']
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0,'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    SPLIT_PARAMS = ['is_win','game_mode','skill_level']
    DOUBLE_PARAMS = [(item,item) for item in SPLIT_PARAMS]

    hero = SingleHeroSelect(required=True)
    player = SinglePlayerField(required=False)
    game_modes = MultiGameModeSelect()
    x_var = forms.ChoiceField(choices=X_LIST, required=True)
    y_var = forms.ChoiceField(choices=Y_LIST, required=True)
    split_var = forms.ChoiceField(choices=DOUBLE_PARAMS, required=True)
    group_var = forms.ChoiceField(choices=DOUBLE_PARAMS, required=True)


class HeroPlayerSkillBarsForm(forms.Form):

    hero = SingleHeroSelect()
    player = SinglePlayerField(required=False)
    game_modes = MultiGameModeSelect()
    levels = forms.MultipleChoiceField(choices=[(i,i) for i in range(1,26)],
        required=True, initial=[6,11,16])

    def clean_levels(self):
        lvls = self.cleaned_data['level']
        return_lvl_list = []
        for lvl in lvls:
            try:
                int_lvl = int(lvl)
                return_lvl_list.append(int_lvl)
            except TypeError:
                raise ValidationError("%s could not be turned into an int"%lvl)
        return return_lvl_list
