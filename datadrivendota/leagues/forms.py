from django import forms
import datetime
from .form_fields import SingleLeagueField


def thirty_days_ago():
    return datetime.date.today() - datetime.timedelta(days=30)


class LeagueWinrateLevers(forms.Form):

    GROUP_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['alignment', 'hero']
    ]
    league = SingleLeagueField(
        help_text=(
            'The name of a single league.  '
            'Use the autocomplete dropdown.'
        )
    )
    min_date = forms.DateField(
        required=False,
        initial=thirty_days_ago,
        help_text='Start times for included games must be on or after this'
    )
    min_date.widget = forms.TextInput(
        attrs={'class': 'datepicker'}
    )
    max_date = forms.DateField(
        required=False,
        initial=datetime.date.today,
        help_text='Start times for included dates must be on or before this'
    )
    max_date.widget = forms.TextInput(
        attrs={'class': 'datepicker'}
    )
    group_var = forms.ChoiceField(
        choices=GROUP_CHOICES,
        required=True,
        help_text='How should we color the dots?'
    )
