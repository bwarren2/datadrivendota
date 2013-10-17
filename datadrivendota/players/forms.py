from django import forms
import datetime
from matches.form_fields import MultiGameModeSelect
from .form_fields import SinglePlayerField

thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

class PlayerWinrateLevers(forms.Form):

    thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
    player = SinglePlayerField()
    game_modes = MultiGameModeSelect(required=True)
    min_date = forms.DateField(required=False, initial=thirty_days_ago)
    min_date.widget=forms.TextInput(attrs={'class':'datepicker'})
    max_date = forms.DateField(required=False, initial=datetime.date.today)
    max_date.widget=forms.TextInput(attrs={'class':'datepicker'})



class PlayerTimelineForm(forms.Form):

    PLOT_CHOICES = [(item, item.replace("_"," ").title()) for item in ['winrate','count']]
    TIME_CHOICES = [(item, item.replace("_"," ").title()) for item in ['date','hour_of_day','month','week']]
    player = SinglePlayerField()
    bucket_var = forms.ChoiceField(choices=TIME_CHOICES, required=True)
    plot_var = forms.ChoiceField(choices=PLOT_CHOICES, required=True)


    min_date = forms.DateField(required=False, initial=thirty_days_ago)
    min_date.widget=forms.TextInput(attrs={'class':'datepicker'})
    max_date = forms.DateField(required=False, initial=datetime.date.today)
    max_date.widget=forms.TextInput(attrs={'class':'datepicker'})
