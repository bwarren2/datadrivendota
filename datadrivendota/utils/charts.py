
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
        'chart': None,
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
