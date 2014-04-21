from django.core.urlresolvers import reverse
from matches.models import (
    PlayerMatchSummary,
)
from utils.exceptions import NoDataFound
from utils.charts import params_dict, datapoint_dict, color_scale_params
from matches.models import GameMode


def item_endgame(
    hero=None,
    player=None,
    game_modes=[],
    *args, **kwargs
):
    if game_modes == []:
        game_modes = [
            mode.steam_id
            for mode in GameMode.objects.filter(is_competitive=True)
        ]

    if hero is None and player is None:
        raise NoDataFound
    pmses = PlayerMatchSummary.objects.all()
    if hero is not None:
        pmses = pmses.filter(hero__steam_id=hero)
    if player is not None:
        pmses = pmses.filter(player__steam_id=player)

    itemDict = {}
    pmses = pmses.select_related()
    for p in pmses:
        for attr in [
            'item_0',
            'item_1',
            'item_2',
            'item_3',
            'item_4',
            'item_5'
        ]:
            itm = getattr(p, attr)
            if itm not in itemDict:
                itemDict[itm] = {
                    'wins': set(),
                    'losses': set(),
                }
            if p.is_win:
                itemDict[itm]['wins'].add(p.match.steam_id)
            else:
                itemDict[itm]['losses'].add(p.match.steam_id)
    datalist = []
    for itm in itemDict:
        itemDict[itm]['games'] = \
            len(itemDict[itm]['losses']) + len(itemDict[itm]['wins'])
        denominator = 1 if itemDict[itm]['games'] == 0 \
            else itemDict[itm]['games']
        itemDict[itm]['winrate'] = len(itemDict[itm]['wins'])\
            / float(denominator) * 100

        datadict = datapoint_dict()
        datadict.update({
            'x_var': itemDict[itm]['games'],
            'y_var': itemDict[itm]['winrate'],
            'label': itm.name,
            'tooltip': itm.name,
            'split_var': '',
            'group_var': '',
            'point_size': itm.cost,
            # 'url': reverse(
            #     'items:detail',
            #     kwargs={'item_name': itm.name}
            # )
        })
        datalist.append(datadict)

    if len(datalist) == 0:
        raise NoDataFound

    params = params_dict()
    params['x_min'] = 0
    params['x_max'] = max([d['x_var'] for d in datalist])
    params['y_min'] = 0
    params['y_max'] = 100
    params['legendWidthPercent'] = .25
    params['x_label'] = 'Games'
    params['y_label'] = 'Winrate'
    params['margin']['left'] = 12*len(str(params['y_max']))
    params['chart'] = 'xyplot'
    params['pointDomainMin'] = 0
    params['pointDomainMax'] = 5000
    params['pointSizeMin'] = 2
    params['pointSizeMax'] = 5
    params = color_scale_params(params, [d['label'] for d in datalist])
    return (datalist, params)
