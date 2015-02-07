from model_mommy.recipe import seq, Recipe
from .models import Team

team = Recipe(
    Team,
    steam_id=seq(1)
    )
