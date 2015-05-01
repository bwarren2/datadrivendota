from django import forms
from django.forms.widgets import CheckboxSelectMultiple
import datetime
from matches.form_fields import MultiGameModeSelect
from .form_fields import SinglePlayerField
from heroes.models import Role
from heroes.form_fields import SingleHeroSelect


def thirty_days_ago():
    return datetime.date.today() - datetime.timedelta(days=30)


def get_roles():
    return [
        (role.name, role.name.replace("_", " ").title())
        for role in Role.objects.all()
    ]


class PlayerWinrateLevers(forms.Form):

    def init(self, *args, **kwargs):
        super(PlayerWinrateLevers, self).init(*args, **kwargs)
        self.fields['role_list'] = forms.MultipleChoiceField(
            choices=get_roles(),
            required=False,
            help_text='Pick one or more stats to graph',
            widget=CheckboxSelectMultiple
        )
        self.game_modes.setup()

    GROUP_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['hero', 'alignment']
    ]
    player = SinglePlayerField(
        help_text=(
            'The name of a single player.  '
            'Use the autocomplete dropdown.'
        )
    )
    game_modes = MultiGameModeSelect(
        required=True,
        help_text='Which modes would you like to include?'
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


class PlayerAdversarialForm(forms.Form):
    GROUP_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['hero', 'alignment']
    ]
    DISPLAY_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['winrate', 'usage']
    ]

    player = SinglePlayerField(
        help_text=(
            'The name of a single player.  '
            'Use the autocomplete dropdown.'
        )
    )
    game_modes = MultiGameModeSelect(
        required=True,
        help_text='Which modes would you like to include?'
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
    plot_var = forms.ChoiceField(
        choices=DISPLAY_CHOICES,
        required=True,
        help_text='Winrate or games?'
    )


class PlayerTimelineForm(forms.Form):
    PLOT_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['winrate', 'count']
    ]
    TIME_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['date', 'hour_of_day', 'month', 'week']
    ]

    player = SinglePlayerField(
        help_text='Pick exactly one player.  Use the autocomplete.'
    )
    bucket_var = forms.ChoiceField(
        choices=TIME_CHOICES,
        required=True,
        help_text='How much time should go in each bar?'
    )
    plot_var = forms.ChoiceField(
        choices=PLOT_CHOICES,
        required=True,
        help_text='What would you like to chart?'
    )
    min_date = forms.DateField(
        required=False,
        initial=thirty_days_ago,
        help_text='Start times for included games must be on or after this'
    )
    min_date.widget = forms.TextInput(attrs={'class': 'datepicker'})
    max_date = forms.DateField(
        required=False,
        initial=datetime.date.today,
        help_text='Start times for included dates must be on or before this'
    )
    max_date.widget = forms.TextInput(attrs={'class': 'datepicker'})


class PlayerAddFollowForm(forms.Form):
    player = SinglePlayerField(
        required=True,
        help_text='Pick exactly one player.  Use the autocomplete.'
    )


class HeroAbilitiesForm(forms.Form):
    player_1 = SinglePlayerField(
        required=True,
        help_text='Pick exactly one player.  Use the autocomplete.'
    )
    hero_1 = SingleHeroSelect(
        required=True,
        help_text='Pick exactly one hero.  Use the autocomplete.'
    )
    player_2 = SinglePlayerField(
        required=False,
        help_text='Pick up to one player.  Use the autocomplete.'
    )
    hero_2 = SingleHeroSelect(
        required=False,
        help_text='Pick up to one hero.  Use the autocomplete.'
    )
    game_modes = MultiGameModeSelect(
        required=True,
        help_text='Which modes would you like to include?'
    )
    division = forms.ChoiceField(
        choices=[
            ('Players', 'Players'),
            ('Win/loss', 'Win/loss'),
            ('Player win/loss', 'Player win/loss')
            ],
        required=True,
        help_text='How should the datasets be partitioned?'
    )


class VersusWinrateForm(forms.Form):
    GROUP_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['hero', 'alignment']
    ]
    DISPLAY_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['winrate', 'usage']
    ]
    player_1 = SinglePlayerField(
        required=True,
        help_text='Pick exactly one player.  Use the autocomplete.'
    )
    player_2 = SinglePlayerField(
        required=False,
        help_text='Pick up to one player.  Use the autocomplete.'
    )
    game_modes = MultiGameModeSelect(
        required=True,
        help_text='Which modes would you like to include?'
    )
    min_date = forms.DateField(
        required=False,
        initial=thirty_days_ago,
        help_text='Start times for included games must be on or after this'
    )
    min_date.widget = forms.TextInput(attrs={'class': 'datepicker'})
    max_date = forms.DateField(
        required=False,
        initial=datetime.date.today,
        help_text='Start times for included dates must be on or before this'
    )
    max_date.widget = forms.TextInput(attrs={'class': 'datepicker'})
    group_var = forms.ChoiceField(
        choices=GROUP_CHOICES,
        required=True,
        help_text='How should we color the dots?'
    )
    plot_var = forms.ChoiceField(
        choices=DISPLAY_CHOICES,
        required=True,
        help_text='Winrate or games?'
    )


class RoleForm(forms.Form):
    DISPLAY_CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['winrate', 'performance', 'games']
    ]
    player_1 = SinglePlayerField(
        required=True,
        help_text='Pick exactly one player.  Use the autocomplete.'
    )
    player_2 = SinglePlayerField(
        required=False,
        help_text='Pick up to one player.  Use the autocomplete.'
    )
    plot_var = forms.ChoiceField(
        choices=DISPLAY_CHOICES,
        required=True,
        help_text='Winrate or games?'
    )


class PlayerMatchesFilterForm(forms.Form):
    hero = SingleHeroSelect(
        required=True,
        help_text='Pick exactly one hero.  Use the autocomplete.'
    )
    min_date = forms.DateField(
        required=False,
        initial=thirty_days_ago,
        help_text='Start times for included games must be on or after this'
    )
    min_date.widget = forms.TextInput(attrs={'class': 'datepicker'})
    max_date = forms.DateField(
        required=False,
        initial=datetime.date.today,
        help_text='Start times for included dates must be on or before this'
    )
    max_date.widget = forms.TextInput(attrs={'class': 'datepicker'})
