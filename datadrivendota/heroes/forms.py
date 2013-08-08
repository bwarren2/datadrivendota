from django import forms
from heroes.models import HeroDossier
from django.contrib.admin.widgets import FilteredSelectMultiple


heroes = HeroDossier.objects.all().order_by('hero__name')
hero_list = [(dossier.hero.name, dossier.hero.name) for dossier in heroes]

vital_stats = ['strength', 'intelligence', 'agility', 'modified_armor', 'effective_hp',
               'hp', 'mana']
vital_stats = [(item, item) for item in vital_stats]


class HeroVitalsMultiSelect(forms.Form):

    heroes = forms.MultipleChoiceField(choices=hero_list, widget=FilteredSelectMultiple("verbose name", is_stacked=False))
    stats = forms.MultipleChoiceField(choices=vital_stats, widget=FilteredSelectMultiple("verbose name", is_stacked=False))

