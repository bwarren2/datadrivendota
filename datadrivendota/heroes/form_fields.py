from django import forms
from django.forms import ValidationError
from heroes.models import Hero


class SingleHeroSelect(forms.CharField):
    widget=forms.TextInput(attrs={'class': 'single-hero-tags',})
    def clean(self, hero):
        if ',' in hero:
            raise ValidationError("Only one hero at a time.")
        try:
            hero = Hero.objects.get(name=hero)
        except Hero.DoesNotExist:
            raise ValidationError("No hero by that name.")

        return hero.steam_id

class MultiHeroSelect(forms.CharField):
    widget=forms.TextInput(attrs={'class': 'multi-hero-tags',})
    def clean(self, hero_str):
        print hero_str, "," in hero_str
        if ',' not in hero_str:
            try:
                hero = Hero.objects.get(name=hero_str)
            except Hero.DoesNotExist:
                raise ValidationError("%s is not a valid hero name" % hero)
            return [hero.steam_id]

        else:
            hero_list = hero_str.split(',')
            return_hero_list = []
            for hero in hero_list:
                try:
                    hero = Hero.objects.get(name=hero)
                except Hero.DoesNotExist:
                    raise ValidationError("%s is not a valid hero name" % hero)
                return_hero_list.append(hero.steam_id)
            return return_hero_list
