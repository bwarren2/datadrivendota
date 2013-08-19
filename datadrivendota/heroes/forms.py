from django import forms
from heroes.models import HeroDossier


heroes = HeroDossier.objects.all().order_by('hero__name')
hero_list = [(dossier.hero.name, dossier.hero.name) for dossier in heroes]

vital_stats = ['strength', 'intelligence', 'agility', 'modified_armor', 'effective_hp',
               'hp', 'mana']
vital_stats = [(item, item) for item in vital_stats]


class HeroVitalsMultiSelect(forms.Form):

    heroes = forms.MultipleChoiceField(choices=hero_list, required=True)
    stats = forms.MultipleChoiceField(choices=vital_stats, required=True)

