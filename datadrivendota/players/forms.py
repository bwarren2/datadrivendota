from django import forms
import datetime
from matches.form_fields import MultiGameModeSelect
from .form_fields import SinglePlayerField

thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

class PlayerWinrateLevers(forms.Form):

    player = SinglePlayerField(
        help_text='The name of a single player.  Use the autocomplete dropdown.')
    game_modes = MultiGameModeSelect(required=True,
        help_text='Which modes would you like to include?')
    min_date = forms.DateField(required=False, initial=thirty_days_ago,
        help_text='Start times for included games must be on or after this')
    min_date.widget=forms.TextInput(attrs={'class':'datepicker'})
    max_date = forms.DateField(required=False, initial=datetime.date.today,
        help_text='Start times for included dates must be on or before this')
    max_date.widget=forms.TextInput(attrs={'class':'datepicker'})



class PlayerTimelineForm(forms.Form):

    PLOT_CHOICES = [(item, item.replace("_"," ").title()) for item in ['winrate','count']]
    TIME_CHOICES = [(item, item.replace("_"," ").title()) for item in ['date','hour_of_day','month','week']]

    player = SinglePlayerField(help_text='Pick exactly one player.  Use the autocomplete.')
    bucket_var = forms.ChoiceField(choices=TIME_CHOICES, required=True,
        help_text='How much time should go in each bar?')
    plot_var = forms.ChoiceField(choices=PLOT_CHOICES, required=True,
        help_text='What would you like to chart?')
    min_date = forms.DateField(required=False, initial=thirty_days_ago,
        help_text='Start times for included games must be on or after this')
    min_date.widget=forms.TextInput(attrs={'class':'datepicker'})
    max_date = forms.DateField(required=False, initial=datetime.date.today,
        help_text='Start times for included dates must be on or before this')
    max_date.widget=forms.TextInput(attrs={'class':'datepicker'})

class PlayerAddFollowForm(forms.Form):
    player = SinglePlayerField(required=True,
        help_text='Pick exactly one player.  Use the autocomplete.')
