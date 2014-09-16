from django import forms
from django.forms import ValidationError
from heroes.models import Hero


class SingleHeroSelect(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-hero-tags'})

    def clean(self, hero):
        if self.required and not hero:
            raise forms.ValidationError("That is not a real hero name")
        if not self.required and not hero:
            return None

        if ',' in hero:
            raise ValidationError("Only one hero at a time.")
        try:
            num_id = int(hero)
            hero = Hero.objects.get(steam_id=num_id)
        except Hero.DoesNotExist:
            raise ValidationError("No hero by that ID.")

        return hero.steam_id


class MultiHeroSelect(forms.CharField):
    """ Takes a comma-delimited string and returns a list of all the instances with names in that list."""

    widget = forms.HiddenInput(attrs={'class': 'multi-hero-tags'})

    def clean(self, hero_str):
        if self.required and not hero_str:
            raise forms.ValidationError("That is not a real hero name")
        if not self.required and not hero_str:
            return None

        hero_list = hero_str.split(',')
        return_hero_list = []
        for hero in hero_list:
            try:
                hero = Hero.objects.get(steam_id=hero)
            except Hero.DoesNotExist:
                raise ValidationError("%s is not a valid hero name" % hero)
            return_hero_list.append(hero.steam_id)
        return return_hero_list


class MultiLeveLSelect(forms.MultipleChoiceField):
    widget = forms.SelectMultiple(attrs={'class': 'multi-level-tags'})
