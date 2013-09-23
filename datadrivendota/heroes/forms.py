from django import forms
from heroes.models import HeroDossier, Hero
from django_select2 import AutoModelSelect2MultipleField

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


class HeroMultiSelect(AutoModelSelect2MultipleField):
    queryset = Hero.objects
    search_fields = ['name__icontains']

    class Meta:
        model = Hero


class HeroVitalsMultiSelect(forms.Form):

    heroes = HeroMultiSelect(required=True)
#    heroes = forms.MultipleChoiceField(choices=hero_list, required=True)
    stats = forms.MultipleChoiceField(choices=vital_stats, required=True)


class HeroLineupMultiSelect(forms.Form):
    heroes = forms.MultipleChoiceField(choices=hero_list, required=True)
    heroes.widget=forms.TextInput(attrs={'class': 'tags',})
    stats = forms.ChoiceField(choices=lineup_stats, required=True)
    level = forms.ChoiceField(choices=[(i,i) for i in range(1,26)], required=True)

