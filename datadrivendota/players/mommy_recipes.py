from model_mommy.recipe import Recipe, seq
from players.models import Player


player = Recipe(
    Player,
    steam_id=seq(1),
)
