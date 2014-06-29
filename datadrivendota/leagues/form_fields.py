from django import forms
from .models import League
from django.core.exceptions import MultipleObjectsReturned


class SingleLeagueField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-league-tags'})

    def clean(self, league_id):
        if self.required and not league_id:
            raise forms.ValidationError("That is not a real league name")
        if not self.required and not league_id:
            return None
        if "," in league_id:
            raise forms.ValidationError(
                "Only one league please. "
                "Commas in names also trigger this error."
            )
        try:
            league = League.objects.get(steam_id=league_id)
        except League.DoesNotExist:
            raise forms.ValidationError("I do not have a league by that name")
        except MultipleObjectsReturned:
            raise forms.ValidationError(
                "I could not uniquely identify that league"
            )
        return league.steam_id
