from .json_data import item_endgame
from .forms import ItemWinrateForm


class ItemWinrateMixin(object):
    form = ItemWinrateForm
    attrs = [
        'hero',
        'player',
        'game_modes',
        'skill_level',
    ]
    json_function = staticmethod(item_endgame)
