from django import forms
from django.forms.widgets import CheckboxSelectMultiple
import datetime
from .form_fields import SingleTeamField
from heroes.models import Role


def thirty_days_ago():
    return datetime.date.today() - datetime.timedelta(days=30)


def get_roles():
    return [
        (role.name, role.name.replace("_", " ").title())
        for role in Role.objects.all()
    ]


class TeamWinrateLevers(forms.Form):

    def init(self, *args, **kwargs):
        super(TeamWinrateLevers, self).init(*args, **kwargs)
        self.fields['role_list'] = forms.MultipleChoiceField(
            choices=get_roles(),
            required=False,
            help_text='Pick one or more stats to graph',
            widget=CheckboxSelectMultiple
        )

    GROUP_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['alignment', 'hero']
    ]
    team = SingleTeamField(
        help_text=(
            'The name of a single team.  '
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
