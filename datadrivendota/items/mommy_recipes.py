from model_mommy.recipe import Recipe, seq
from items.models import Item

item = Recipe(
    Item,
    steam_id=seq(1),
    name=seq('Item'),
    )
