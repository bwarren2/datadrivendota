from django.conf import settings
from heroes.models import Hero
from django.utils.text import slugify
import json



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


def hero_classes_dict():
    hero_data = Hero.objects.all().values(
        'steam_id',
        'herodossier__alignment',
        'assignment__role__name',
        'name'
    )

    hero_classes = {}
    for dct in hero_data:
        idx = dct['steam_id']
        if idx not in hero_classes:
            hero_classes[idx] = set()
        if dct['herodossier__alignment'] is not None:
            hero_classes[idx].add(slugify(dct['herodossier__alignment']))
        if dct['assignment__role__name'] is not None:
            hero_classes[idx].add(slugify(dct['assignment__role__name']))
        if dct['name'] is not None:
            hero_classes[idx].add(slugify(dct['name']))

    return hero_classes


def valid_panel_var(split_var):
    if split_var is not None and split_var != 'None':
        return True
    else:
        return False


def valid_var(var):
    if var is not None and var != 'None':
        return True
    else:
        return False


class ChartGroup(object):
    "A convenience class for constructing things that go in legends"
    display_name = None
    index = None
    color = None
    slug = None

    def __to_dict__(self):
        if self.display_name is None \
                or self.index is None or self.color is None:
            raise Exception
        else:
            return {
                'display_name': self.display_name,
                'index': self.index,
                'color': self.color,
                'class_selector': slugify(unicode(self.slug)),
                #If you have not done this already, it is brutally enforced
            }


class ChartPanel(object):
    "A convenience class for managing chart divisions"
    display_name = None
    original_name = None
    index = None

    def __to_dict__(self):
        if self.display_name is None or self.index is None:
            raise Exception("A panel is not finished!")
        else:
            return {
                'display_name': self.display_name,
                'index': self.index,
            }


class Params(object):
    y_min = None
    y_max = None
    x_label = None
    y_label = None
    draw_path = False
    draw_legend = True
    margin = None
    padding = None
    outerWidth = 400
    outerHeight = 400
    legendWidthPercent = .25
    legendHeightPercent = .1
    pointDomainMin = 1
    pointDomainMax = 1
    pointSizeMin = 5
    pointSizeMax = 5
    strokeDomainMin = 0
    strokeDomainMax = 0
    strokeSizeMin = 1
    strokeSizeMax = 1
    path_stroke_width = 3
    fadeOpacity = .1
    chart = None

    def __init__(self):
        if self.margin is None:
            self.margin = {'top': 25, 'right': 20, 'bottom': 20, 'left': 30}
        if self.padding is None:
            self.padding = {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
        if self.x_label is None:
            self.x_label = 'X Label'
        if self.y_label is None:
            self.y_label = 'Y Label'

    def __to_dict__(self):
        dct = {
            'chart': self.chart,
            'x_label': self.x_label,
            'y_label': self.y_label,
            'draw_path': self.draw_path,
            'draw_legend': self.draw_legend,
            'margin': self.margin,
            'padding': self.padding,
            'outerWidth': self.outerWidth,
            'outerHeight': self.outerHeight,
            'legendWidthPercent': self.legendWidthPercent,
            'legendHeightPercent': self.legendHeightPercent,
            'pointDomainMin': self.pointDomainMin,
            'pointDomainMax': self.pointDomainMax,
            'pointSizeMin': self.pointSizeMin,
            'pointSizeMax': self.pointSizeMax,
            'strokeDomainMin': self.strokeDomainMin,
            'strokeDomainMax': self.strokeDomainMax,
            'strokeSizeMin': self.strokeSizeMin,
            'strokeSizeMax': self.strokeSizeMax,
            'path_stroke_width': self.path_stroke_width,
            'fadeOpacity': self.fadeOpacity,
            'y_min': self.y_min,
            'y_max': self.y_max,
        }
        return dct


class XYParams(Params):
    x_min = None
    x_max = None
    chart = 'xyplot'  # Matters for js plot() dispatch

    def __to_dict__(self):
        parent_dict = super(XYParams, self).__to_dict__()
        parent_dict.update({
            'x_min': self.x_min,
            'x_max': self.x_max,
        })
        return parent_dict


class TasselParams(Params):
    x_min = None
    x_max = None
    path_stroke_width = 1
    chart = 'scatterseries'  # Matters for js plot() dispatch

    def __to_dict__(self):
        parent_dict = super(TasselParams, self).__to_dict__()
        parent_dict.update({
            'x_min': self.x_min,
            'x_max': self.x_max,
            'path_stroke_width': self.path_stroke_width,
        })
        return parent_dict


class BarParams(Params):
    x_set = None
    chart = 'barplot'  # Matters for js plot() dispatch
    tick_values = None

    def __init__(self):
        super(BarParams, self).__init__()

        if self.x_set is None:
            self.x_set = []

    def __to_dict__(self):
        parent_dict = super(BarParams, self).__to_dict__()
        parent_dict.update({
            'x_set': self.x_set,
        })
        if self.tick_values is not None:
            parent_dict.update({
                'tick_values': self.tick_values,
            })
        return parent_dict


class DataPoint(object):
    "Core data class for charts."
    x_var = None
    y_var = None
    panel_var = None
    group_var = None
    label = None
    tooltip = None
    url = None
    point_size = 1
    stroke_width = 1
    classes = None

    def __init__(self):
        if self.classes is None:
            self.classes = []

    def __to_dict__(self):
        return {
            'x_var': self.x_var,
            'y_var': self.y_var,
            'panel_var': self.panel_var,
            'group_var': self.group_var,
            'label': self.label,
            'tooltip': self.tooltip,
            'url': self.url,
            'point_size': self.point_size,
            'stroke_width': self.stroke_width,
            'classes': self.classes,
        }


class TasselDataPoint(DataPoint):
    "Tassels have three ordering layers while regular charts have two,"
    " so we add one here."
    series_var = None

    def __to_dict__(self):
        parent_dict = super(TasselDataPoint, self).__to_dict__()
        parent_dict.update({
            'series_var': self.series_var,
        })
        return parent_dict


class Chart(object):
    groups = None
    panels = None
    chart_groups = None
    chart_panels = None
    params = None
    datalist = None

    def __init__(self):
        if self.datalist is None:
            self.datalist = []

    def json_serialize(self):
        return json.dumps(
            {
                'data': [d.__to_dict__() for d in self.datalist],
                'parameters': self.params.__to_dict__(),
                'groups': [d.__to_dict__() for d in self.chart_groups],
                'panels': [d.__to_dict__() for d in self.chart_panels],
            }
        )

    def as_JSON(self):
        self.validate_data()
        self.postprocess()
        self.substitute_data()

        return self.json_serialize()

    def validate_data(self):
        #Any unfinished datapoints are cause for concern
        bad_xs = len(
            [d.x_var for d in self.datalist if d.x_var is None]
        )
        bad_ys = len(
            [d.y_var for d in self.datalist if d.y_var is None]
        )

        if bad_xs > 0:
            raise Exception(
                '{0} datapoints have bad x values'.format(bad_xs)
            )

        if bad_ys > 0:
            raise Exception(
                '{0} datapoints have bad x values'.format(bad_ys)
            )

    def postprocess(self):

        if self.groups is None:
            self.groups = list(set([d.group_var for d in self.datalist]))
        if self.panels is None:
            self.panels = list(set([d.panel_var for d in self.datalist]))

        self.chart_groups = self.structure_groups(self.groups)
        self.chart_panels = self.structure_panels(self.panels)

    def substitute_data(self):
        group_map = {d.original_name: d.index for d in self.chart_groups}
        selector_map = {d.original_name: d.slug for d in self.chart_groups}
        panel_map = {d.original_name: d.index for d in self.chart_panels}

        for d in self.datalist:
            d.classes.append(selector_map[d.group_var])
            d.group_var = group_map[d.group_var]
            d.panel_var = panel_map[d.panel_var]

    @staticmethod
    def structure_groups(groups):
        colors = other_colors()

        chart_group_list = []
        for idx, group in enumerate(groups):
            #When we deal with slug collision,
            #this is where we can put the testing.
            slug = slugify(unicode(group))
            chartgroup = ChartGroup()
            if group is None:
                chartgroup.display_name = ''
            else:
                chartgroup.display_name = group
            chartgroup.original_name = group
            chartgroup.index = idx
            chartgroup.slug = slug
            if standard_color_map(group) is not None:
                chartgroup.color = standard_color_map(group)
            else:
                chartgroup.color = next(colors)
            chart_group_list.append(chartgroup)

        return chart_group_list

    @staticmethod
    def structure_panels(panels):
        chart_panel_list = []

        for idx, panel in enumerate(panels):
            #When we deal with slug collision,
            #this is where we can put the testing.
            chartpanel = ChartPanel()
            if panel is None:
                chartpanel.display_name = ''
            else:
                chartpanel.display_name = panel
            chartpanel.index = idx
            chartpanel.original_name = panel
            chart_panel_list.append(chartpanel)

        return chart_panel_list


class XYPlot(Chart):

    def __init__(self):
        super(XYPlot, self).__init__()
        if self.params is None:
            self.params = XYParams()

    def validate_data(self):
        #Any unfinished datapoints are cause for concern
        super(XYPlot, self).validate_data()

        #Set the min maxes
        if self.params.x_min is None:
            self.params.x_min = min([d.x_var for d in self.datalist])
        if self.params.x_max is None:
            self.params.x_max = max([d.x_var for d in self.datalist])
        if self.params.y_min is None:
            self.params.y_min = min([d.y_var for d in self.datalist])
        if self.params.y_max is None:
            self.params.y_max = max([d.y_var for d in self.datalist])
        self.params.margin['left'] = 9*len(str(round(self.params.y_max)))


class TasselPlot(Chart):

    def __init__(self):
        super(TasselPlot, self).__init__()
        if self.params is None:
            self.params = TasselParams()

    def validate_data(self):
        #Any unfinished datapoints are cause for concern
        super(TasselPlot, self).validate_data()

        #Set the min maxes
        if self.params.x_min is None:
            self.params.x_min = min([d.x_var for d in self.datalist])
        if self.params.x_max is None:
            self.params.x_max = max([d.x_var for d in self.datalist])
        if self.params.y_min is None:
            self.params.y_min = min([d.y_var for d in self.datalist])
        if self.params.y_max is None:
            self.params.y_max = max([d.y_var for d in self.datalist])
        self.params.margin['left'] = 9*len(str(round(self.params.y_max)))


class BarPlot(Chart):

    def __init__(self):
        super(BarPlot, self).__init__()

        if self.params is None:
            self.params = BarParams()

    def validate_data(self):
        super(BarPlot, self).validate_data()

        self.params.x_set = [d.x_var for d in self.datalist]

        #Set the min maxes
        if self.params.y_min is None:
            self.params.y_min = min([d.y_var for d in self.datalist])
        if self.params.y_max is None:
            self.params.y_max = max([d.y_var for d in self.datalist])
