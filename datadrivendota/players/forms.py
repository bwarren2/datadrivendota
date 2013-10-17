from django import forms
import datetime
from matches.form_fields import MultiGameModeSelect
from .form_fields import SinglePlayerField


class PlayerWinrateLevers(forms.Form):

    player = SinglePlayerField()
    game_modes = MultiGameModeSelect(required=True)

    def __init__(self,*args,**kwargs):
        super(PlayerWinrateLevers, self).__init__(*args, **kwargs)

        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)
        self.min_date = forms.DateField(required=False, initial=thirty_days_ago)
        self.min_date.widget=forms.TextInput(attrs={'class':'datepicker'})
        self.max_date = forms.DateField(required=False, initial=datetime.date.today)
        self.max_date.widget=forms.TextInput(attrs={'class':'datepicker'})

class PlayerTimelineForm(forms.Form):

    PLOT_CHOICES = [(item, item.replace("_"," ").title()) for item in ['winrate','count']]
    TIME_CHOICES = [(item, item.replace("_"," ").title()) for item in ['date','hour_of_day','month','week']]
    player = SinglePlayerField()
    bucket_var = forms.ChoiceField(choices=TIME_CHOICES, required=True)
    plot_var = forms.ChoiceField(choices=PLOT_CHOICES, required=True)

    def __init__(self,*args,**kwargs):
        super(PlayerTimelineForm, self).__init__(*args, **kwargs)

        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

        self.min_date = forms.DateField(required=False, initial=thirty_days_ago)
        self.min_date.widget=forms.TextInput(attrs={'class':'datepicker'})
        self.max_date = forms.DateField(required=False, initial=datetime.date.today)
        self.max_date.widget=forms.TextInput(attrs={'class':'datepicker'})
