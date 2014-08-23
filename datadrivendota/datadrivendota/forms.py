import datetime
from django import forms
from players.form_fields import SinglePlayerField
from heroes.form_fields import SingleHeroSelect
from accounts.models import Applicant


def beta_start():
    return datetime.date(2011, 9, 13)


class KeyForm(forms.Form):
    code = forms.CharField()


class FollowMatchForm(forms.Form):
    player = SinglePlayerField(
        required=False,
        help_text='Pick only one player'
    )
    hero = SingleHeroSelect(
        required=False,
        help_text='Pick only one hero'
    )
    min_date = forms.DateField(
        required=False,
        initial=beta_start,
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


class MatchRequestForm(forms.Form):
    match_id = forms.IntegerField(min_value=10000, max_value=10000000000)


class SearchForm(forms.Form):
    search_string = forms.CharField(required=True, max_length=50)


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['email', 'steam_id', 'interested_in_premium']
