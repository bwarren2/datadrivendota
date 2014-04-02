import random
from django.conf import settings

def params_dict():
    dictionary = {
        'x_min': 0,
        'x_max': 0,
        'y_min': 0,
        'y_max': 0,
        'x_label': 'X Label',
        'y_label': 'Y Label',
        'draw_path': False,
        'draw_legend': True,
        'margin': {'top': 25, 'right': 20, 'bottom': 20, 'left': 30},
        'padding': {'top': 0, 'right': 0, 'bottom': 0, 'left': 0},
        'outerWidth': 400,
        'outerHeight': 400,
        'legendWidthPercent': .2,
        'legendHeightPercent': .1,
        'chart': None,
        'path_stroke_width': 3,
    }
    return dictionary


def datapoint_dict():
    dictionary = {
        'x_var': None,
        'y_var': None,
        'split_var': None,
        'group_var': None,
        'label': None,
        'tooltip': None,
        'url': None,
    }
    return dictionary


def color_scale_params(params, group_list):
    colors = other_colors()
    groups = set(group_list)
    color_domain, color_range = [], []
    for group in groups:
        if standard_color_map(group) is not None:
            color_domain.append(group)
            color_range.append(standard_color_map(group))
        else:
            color_domain.append(group)
            color_range.append(next(colors))
    params['color_domain'] = color_domain
    params['color_range'] = color_range
    return params


def other_colors():
    n = 0
    colors = settings.CONTRASTING_10
    while True:
        color = colors[n % len(colors)]
        n += 1
        yield color


def standard_color_map(group):
    if group == 'Won':
        return settings.WON_COLOR
    elif group == 'Lost':
        return settings.LOST_COLOR
    elif group == 'Strength':
            return settings.STRENGTH_COLOR
    elif group == 'Agility':
            return settings.AGILITY_COLOR
    elif group == 'Intelligence':
            return settings.INTELLIGENCE_COLOR
    elif group == 'Radiant':
            return settings.RADIANT_GREEN
    elif group == 'Dire':
            return settings.DIRE_RED
    elif group == 'Low Skill':
            return settings.SKILL1_COLOR
    elif group == 'Medium Skill':
            return settings.SKILL2_COLOR
    elif group == 'High Skill':
            return settings.SKILL3_COLOR
    elif group == 'Player':
            return settings.SKILLPLAYER_COLOR
    else:
        return None
