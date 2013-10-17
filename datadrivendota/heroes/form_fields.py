from django import forms
from django.forms import ValidationError
from heroes.models import Hero


class SingleHeroSelect(forms.CharField):
    widget=forms.TextInput(attrs={'class': 'hero-tags',})

    def clean(self, hero):
        print hero
        try:
            hero = Hero.objects.get(name=hero)
            print hero
        except Hero.DoesNotExist:
            raise ValidationError("WTF")

        return hero.steam_id

class MultiHeroSelect(forms.CharField):
    widget=forms.TextInput(attrs={'class': 'hero-tags',})

    def clean(self, hero_str):
        print hero_str, "," in hero_str
        if ',' not in hero_str:
            try:
                print "Trying"
                hero = Hero.objects.get(name=hero_str)
            except Hero.DoesNotExist:
                print "Failing"
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
