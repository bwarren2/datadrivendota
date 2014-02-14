from uuid import uuid4
from django.core.files import File
from django.conf import settings
from itertools import chain
from rpy2 import robjects
from rpy2.robjects import FloatVector, StrVector
from rpy2.robjects.packages import importr
from matches.models import PlayerMatchSummary, Match, fetch_match_attributes, fetch_attribute_label, fetch_single_attribute
from utils.r import enforceTheme, FailFace
from utils.file_management import s3File
from utils.exceptions import NoDataFound
from json import loads as jsonloads

def EndgameChart(player_list,mode_list,x_var,y_var,split_var,group_var):

    grdevices = importr('grDevices')
    importr('lattice')

    selected_summaries = PlayerMatchSummary.objects.filter(
        player__steam_id__in=player_list,
        match__game_mode__steam_id__in=mode_list,
        match__validity=Match.LEGIT)
    selected_summaries = selected_summaries.select_related()
    if len(selected_summaries)==0:
        return FailFace()
    try:
        x_vector_list, xlab = fetch_match_attributes(selected_summaries, x_var)
        y_vector_list, ylab = fetch_match_attributes(selected_summaries, y_var)
        split_vector_list, split_lab = fetch_match_attributes(selected_summaries, split_var)
        group_vector_list, grouplab = fetch_match_attributes(selected_summaries, group_var)
    except AttributeError:
        return FailFace()

    x_vec = FloatVector(x_vector_list)
    y_vec = FloatVector(y_vector_list)

    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    enforceTheme(robjects)

    robjects.globalenv["xvec"] = x_vec
    robjects.globalenv["yvec"] = y_vec
    robjects.globalenv["splitvar"] = StrVector(split_vector_list)
    robjects.globalenv["groupvar"] = StrVector(group_vector_list)

    rcmd="""print(
        xyplot(yvec~xvec|splitvar,groups=groupvar,type=c('p','r'),
                auto.key=list(lines=T,points=T,corner=c(0,.9),background='white',title='%s'),
                ylab='%s',xlab='%s',
                par.settings=simpleTheme(pch=20,lwd=4),
                scales=list(),

                )
    )"""% (grouplab, ylab, xlab)
    robjects.r(rcmd )

    grdevices.dev_off()
    imagefile.close()
    hosted_file = s3File(imagefile)
    return hosted_file

def TeamEndgameChart(player_list,mode_list,x_var,y_var,split_var,group_var,compressor):

    grdevices = importr('grDevices')
    importr('lattice')
    radiant_matches = Match.objects.filter(game_mode__steam_id__in=mode_list, validity=Match.LEGIT)
    dire_matches = Match.objects.filter(game_mode__steam_id__in=mode_list, validity=Match.LEGIT)
    for player in player_list:
        radiant_matches = radiant_matches.filter(playermatchsummary__player__steam_id=player, playermatchsummary__player_slot__lte=5)
        dire_matches = dire_matches.filter(playermatchsummary__player__steam_id=player, playermatchsummary__player_slot__gte=5)

    if len(radiant_matches) + len(dire_matches)==0:
        return FailFace()
    radiant = PlayerMatchSummary.objects.filter(match__in=radiant_matches,player_slot__lte=5).select_related()
    dire = PlayerMatchSummary.objects.filter(match__in=dire_matches,player_slot__gte=5).select_related()

    pmses = list(chain(radiant,dire))
    x_data = dict([(p.match.steam_id,0) for p in pmses])
    y_data = dict([(p.match.steam_id,0) for p in pmses])
    group_data = dict([(p.match.steam_id, False) for p in pmses])
    split_data = dict([(p.match.steam_id, False) for p in pmses])

    for p in pmses:
        x_data[p.match.steam_id] += fetch_single_attribute(summary=p,
                                    attribute=x_var, compressor=compressor)
        y_data[p.match.steam_id] += fetch_single_attribute(summary=p,
                                    attribute=y_var, compressor=compressor)
        group_data[p.match.steam_id] = fetch_single_attribute(summary=p,
                                    attribute=group_var, compressor=compressor)
        split_data[p.match.steam_id] = fetch_single_attribute(summary=p,
                                    attribute=split_var, compressor=compressor)

    try:
        x_vector_list = [item for item in x_data.itervalues()]
        y_vector_list = [item for item in y_data.itervalues()]
        group_vector_list = [item for item in group_data.itervalues()]
        split_vector_list = [item for item in split_data.itervalues()]
        xlab = fetch_attribute_label(attribute=x_var)
        ylab = fetch_attribute_label(attribute=y_var) + " ({a})".format(a=compressor)
        grouplab = fetch_attribute_label(attribute=group_var)
    except AttributeError:
        return FailFace()

    x_vec = FloatVector(x_vector_list)
    y_vec = FloatVector(y_vector_list)

    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    enforceTheme(robjects)

    robjects.globalenv["xvec"] = x_vec
    robjects.globalenv["yvec"] = y_vec
    robjects.globalenv["splitvar"] = StrVector(split_vector_list)
    robjects.globalenv["groupvar"] = StrVector(group_vector_list)

    rcmd="""print(
        xyplot(yvec~xvec|splitvar,groups=groupvar,type=c('p','r'),
                auto.key=list(lines=T,points=T,corner=c(0,.9),background='white',title='%s'),
                ylab='%s',xlab='%s',
                par.settings=simpleTheme(pch=20,lwd=4),
                scales=list(),

                )
    )"""% (grouplab, ylab, xlab)
    robjects.r(rcmd )

    grdevices.dev_off()
    imagefile.close()
    hosted_file = s3File(imagefile)
    return hosted_file


def MatchParameterScatterplot(match_id, x_var, y_var):
    pms = PlayerMatchSummary.objects.filter(match__steam_id=match_id).select_related()
    if len(pms) == 0:
        return FailFace()
    try:
        x, x_lab =  fetch_match_attributes(pms, x_var)
        y, y_lab =  fetch_match_attributes(pms, y_var)
        groups, group_lab =  fetch_match_attributes(pms, 'which_side')
        if groups[0]=='Radiant':
            color=[settings.RADIANT_GREEN,settings.DIRE_RED]
        else:
            color=[settings.DIRE_RED,settings.RADIANT_GREEN]
    except AttributeError:
        return FailFace()

    labels, blank =  fetch_match_attributes(pms, 'hero_name')
    x_vec = FloatVector(x)
    y_vec = FloatVector(y)
    group_vec = StrVector(groups)
    color_vec = StrVector(color)
    labels = robjects.StrVector(fetch_match_attributes(pms, 'hero_name')[0])

    robjects.globalenv["xvec"] = x_vec
    robjects.globalenv["yvec"] = y_vec
    robjects.globalenv["labels"] = labels
    robjects.globalenv["groupvec"] = group_vec
    robjects.globalenv["colorvec"] = color_vec

    grdevices = importr('grDevices')
    importr('lattice')

    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=400,height=350)
    enforceTheme(robjects)

    rcmd="""
    print(
        xyplot(yvec~xvec,groups=groupvec,
                par.settings=simpleTheme(pch=20,lwd=4,col=colorvec),
                ylab='%s',xlab='%s',
                auto.key=list(points=T,corner=c(0,.9),background='white',pch=20),
                panel=function(x, y, ...) {
                    panel.xyplot(x, y, ...);
                    ltext(x=x, y=y, labels=labels, pos=1, offset=0, cex=0.8)
                }
        )
    )"""% (y_lab, x_lab)
    robjects.r(rcmd)
    grdevices.dev_off()

    imagefile.close()

    hosted_file = s3File(imagefile)
    return hosted_file

def MatchAbilityTimeline(json_data, width=800, height=400):
    input_data= jsonloads(json_data)
    x = input_data['x_var']
    y = input_data['y_var']
    group = input_data['group_var']
    split = input_data['split_var']

    if len(x) == 0 or len(y)==0 or len(group) == 0 or len(split)==0:
        raise NoDataFound
    x_vec = FloatVector(x)
    y_vec = FloatVector(y)
    group_vec = StrVector(group)
    split_vec = StrVector(split)

    robjects.globalenv["xvec"] = x_vec
    robjects.globalenv["yvec"] = y_vec
    robjects.globalenv["groupvec"] = group_vec
    robjects.globalenv["splitvec"] = split_vec

    grdevices = importr('grDevices')
    importr('lattice')


    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=width,height=height)
    enforceTheme(robjects)

    #if there are lots of panels, and keys would get in the way/be redundant
    if len(set(split)) > 5:
        rcmd="""
        splitvec = factor(splitvec,levels=unique(splitvec),ordered=T)
        print(
            xyplot(yvec~xvec|splitvec,type=c('p','l'),groups=groupvec,
                    ylab='%s',xlab='%s',
            )
        )"""% (input_data['y_lab'], input_data['x_lab'])
    else:
        rcmd="""
        print(
            xyplot(yvec~xvec|splitvec,type=c('p','l'),groups=groupvec,
                    ylab='%s',xlab='%s',
                    auto.key=list(lines=T,points=T,corner=c(0,.9),background='transparent')
            )
        )"""% (input_data['y_lab'], input_data['x_lab'])

    # rcmd="""
    # print(
    #     xyplot(yvec~xvec|splitvec,type=c('p','l'),groups=groupvec,
    #             ylab='{y_lab}',xlab='{x_lab}',
    #             auto.key=list(lines=T,points=T,corner=c(0,.9),background='transparent'),
    #             panel=function(x, y, ...) {
    #                 panel.xyplot(x, y, ...);
    #             }

    #     )
    # )""".format(x_lab=input_data['x_lab'],y_lab=input_data['y_lab'])

    robjects.r(rcmd)
    grdevices.dev_off()

    imagefile.close()

    hosted_file = s3File(imagefile)
    return hosted_file


