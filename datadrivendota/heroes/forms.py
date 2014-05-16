import datetime
from django import forms
from django.forms import ValidationError
from django.forms.widgets import CheckboxSelectMultiple
from matches.form_fields import MultiGameModeSelect
from players.form_fields import SinglePlayerField
from .form_fields import MultiHeroSelect, SingleHeroSelect, MultiLeveLSelect
from utils import list_to_choice_list
thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)


def thirty_days_ago():
    return datetime.date.today() - datetime.timedelta(days=30)


class HeroVitalsMultiSelect(forms.Form):
    VITAL_STAT_POOL = [
        'strength',
        'intelligence',
        'agility',
        'armor',
        'effective_hp',
        'hp',
        'mana',
    ]
    VITAL_STATS = list_to_choice_list(VITAL_STAT_POOL)

    heroes = MultiHeroSelect(
        required=True,
        help_text='Pick one or more heroes'
    )
    stats = forms.MultipleChoiceField(
        choices=VITAL_STATS,
        required=True,
        help_text='Pick one or more stats to graph',
        widget=CheckboxSelectMultiple
    )
    # unlinked_scales = forms.BooleanField(
    #     required=False,
    #     help_text=(
    #         'The graph scales match across panels by default. '
    #         'Want them to render independently?'
    #     )
    # )


class HeroLineupMultiSelect(forms.Form):

    VITAL_STAT_POOL = [
        'strength',
        'intelligence',
        'agility',
        'modified_armor',
        'effective_hp',
        'hp',
        'mana',
        'day_vision',
        'night_vision',
        'atk_point',
        'atk_backswing',
        'turn_rate',
        'movespeed',
        'projectile_speed',
        'range',
        'base_atk_time',
    ]

    LINEUP_STATS = list_to_choice_list(VITAL_STAT_POOL)
    heroes = MultiHeroSelect(
        required=True,
        help_text='Pick one or more heroes'
    )
    stat = forms.ChoiceField(
        choices=LINEUP_STATS,
        required=True,
        help_text='Pick one stat to graph'
    )
    level = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 26)],
        required=True,
        help_text='Pick which level to graph'
    )

    def clean_level(self):
        lvl = self.cleaned_data['level']
        try:
            int_lvl = int(lvl)
        except TypeError:
            raise ValidationError(
                "{lvl} could not be turned into an int".format(lvl=lvl)
            )
        return int_lvl


class HeroPlayerPerformance(forms.Form):

    SHARED_PARAMETERS = [
        'kills',
        'deaths',
        'assists',
        'gold_total',
        'xp_total',
        'last_hits',
        'denies',
        'hero_damage',
        'tower_damage',
        'hero_healing',
        'level',
        'K-D+.5*A',
    ]
    X_PARAMETERS = list(SHARED_PARAMETERS)
    X_PARAMETERS.insert(0, 'duration')
    X_LIST = [(item, item) for item in X_PARAMETERS]
    Y_LIST = [(item, item) for item in SHARED_PARAMETERS]
    SPLIT_PARAMS = ['is_win', 'game_mode', 'skill_name', None]
    DOUBLE_PARAMS = [(item, item) for item in SPLIT_PARAMS]

    hero = SingleHeroSelect(
        required=True,
        help_text='Pick only one hero'
    )
    player = SinglePlayerField(
        required=False,
        help_text='Pick only one player'
    )
    game_modes = MultiGameModeSelect(
        help_text='Which game modes would you like to sample?'
    )
    x_var = forms.ChoiceField(
        choices=X_LIST, initial='duration',
        required=True,
        help_text='What goes on the x axis?'
    )
    y_var = forms.ChoiceField(
        choices=Y_LIST,
        required=True,
        help_text='What goes on the Y axis?'
    )
    panel_var = forms.ChoiceField(
        choices=DOUBLE_PARAMS,
        initial='is_win',
        required=True,
        help_text=(
            "Which variable breaks out the panels? "
            "Skill is valve's estimation of skill for teams in that match. "
            "1 is normal, 2 is high, 3 is very high."
        )
    )
    group_var = forms.ChoiceField(
        choices=DOUBLE_PARAMS,
        initial='skill_level',
        required=True,
        help_text=(
            "Which variable groups within a panel? "
            "Skill is valve's estimation of skill for teams in that match. "
            "1 is normal, 2 is high, 3 is very high."
        )
    )


class HeroPlayerSkillBarsForm(forms.Form):

    hero = SingleHeroSelect(
        help_text='Pick exactly one hero'
    )
    player = SinglePlayerField(
        required=False,
        help_text='Optionally, pick one player'
    )
    game_modes = MultiGameModeSelect(
        help_text='Which game modes would you like to sample?'
    )
    levels = MultiLeveLSelect(
        choices=[(i, i) for i in range(1, 26)],
        required=True,
        initial=[6, 11, 16],
        help_text='Levels would you like to see?'
    )

    def clean_levels(self):
        lvls = self.cleaned_data['levels']
        return_lvl_list = []
        for lvl in lvls:
            try:
                int_lvl = int(lvl)
                return_lvl_list.append(int_lvl)
            except TypeError:
                raise ValidationError(
                    "{lvl} could not be turned into an int".format(lvl=lvl)
                )
        return return_lvl_list


class HeroProgressionForm(forms.Form):
    hero = SingleHeroSelect(
        help_text='Pick exactly one hero'
    )
    player = SinglePlayerField(
        required=False,
        help_text='Optionally, pick one player'
    )
    game_modes = MultiGameModeSelect(
        help_text='Which game modes would you like to sample?'
    )
    division = forms.ChoiceField(
        choices=[
            ('Skill', 'Skill'),
            ('Win/loss', 'Win/loss'),
            ('Skill win/loss', 'Skill win/loss')
            ],
        required=True,
        help_text='How should the datasets be partitioned?'
    )


class HeroBuildForm(forms.Form):
    hero = SingleHeroSelect(
        help_text='Pick exactly one hero'
    )
    player = SinglePlayerField(
        help_text='Optionally, pick one player'
    )
    game_modes = MultiGameModeSelect(
        help_text='Which game modes would you like to sample?'
    )
    levels = MultiLeveLSelect(
        choices=[(i, i) for i in range(1, 26)],
        required=True,
        initial=[5, 10, 15],
        help_text='Which levels would you like to see?'
    )


class UpdatePlayerWinrateForm(forms.Form):

    hero = SingleHeroSelect(
        required=True,
        help_text='Pick only one hero'
    )
    game_modes = MultiGameModeSelect(
        help_text='Which game modes would you like to sample?'
    )


class HeroPerformanceLineupForm(forms.Form):
    STAT_POOL = [
        'kills',
        'deaths',
        'assists',
        'xp_per_min',
        'gold_per_min',
    ]
    Y_LIST = list_to_choice_list(STAT_POOL)
    SKILL_LEVELS = [
        (1, 'Low Skill'),
        (2, 'Medium Skill'),
        (3, 'High Skill'),
    ]
    IS_WIN_LIST = ['win', 'loss', 'both']
    IS_WIN_CHOICES = list_to_choice_list(IS_WIN_LIST)

    stat = forms.ChoiceField(
        choices=Y_LIST,
        required=True,
        help_text='What goes on the Y axis?'
    )
    skill_level = forms.ChoiceField(
        choices=SKILL_LEVELS,
        required=True,
        help_text='What goes on the Y axis?'
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
    is_win = forms.ChoiceField(
        choices=IS_WIN_CHOICES,
        required=True,
        help_text='Games where they win, lose, or both?'
    )
    heroes = MultiHeroSelect(
        required=True,
        help_text='Pick one or more heroes'
    )
