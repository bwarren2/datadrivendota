from django import forms
from .models import League
from django.core.exceptions import MultipleObjectsReturned
from urllib import unquote


class SingleLeagueField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-league-tags'})

    def clean(self, league_name):
        if self.required and not league_name:
            raise forms.ValidationError("That is not a real league name")
        if not self.required and not league_name:
            return None
        if "," in league_name:
            raise forms.ValidationError(
                "Only one league please. "
                "Commas in names also trigger this error."
            )
        league_name = unquote(league_name)
        try:
            league = League.objects.get(leaguedossier__name=league_name)
        except League.DoesNotExist:
            raise forms.ValidationError("I do not have a league by that name")
        except MultipleObjectsReturned:
            raise forms.ValidationError(
                "I could not uniquely identify that league"
            )
        return league.steam_id

