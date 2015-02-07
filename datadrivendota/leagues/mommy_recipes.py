from model_mommy.recipe import Recipe, seq, foreign_key
from .models import League, ScheduledMatch
from teams.mommy_recipes import team

league = Recipe(
    League, steam_id=seq(1)
    )


scheduled_match = Recipe(
    ScheduledMatch,
    league=foreign_key(league),
    team_1=foreign_key(team),
    team_2=foreign_key(team),
    )
