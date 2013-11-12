from uuid import uuid4
from django.core.files import File
from rpy2 import robjects
from rpy2.robjects import FloatVector, StrVector
from rpy2.robjects.packages import importr
from matches.models import PlayerMatchSummary
from datadrivendota.r import enforceTheme, s3File, FailFace
from datadrivendota.utilities import safen

def EndgameChart(player_list,mode_list,x_var,y_var,split_var,group_var):

    grdevices = importr('grDevices')
    importr('lattice')

    selected_summaries = PlayerMatchSummary.objects.filter(
        player__steam_id__in=player_list,
        match__game_mode__steam_id__in=mode_list)
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

def MatchParameterScatterplot(match_id, x_var, y_var):
    pms = PlayerMatchSummary.objects.filter(match__steam_id=match_id)
    if len(pms) == 0:
        return FailFace()
    try:
        x, x_lab =  fetch_match_attributes(pms, x_var)
        y, y_lab =  fetch_match_attributes(pms, y_var)
    except AttributeError:
        return FailFace()

    labels, blank =  fetch_match_attributes(pms, 'hero_name')
    x_vec = FloatVector(x)
    y_vec = FloatVector(y)
    labels = robjects.StrVector(fetch_match_attributes(pms, 'hero_name')[0])

    robjects.globalenv["xvec"] = x_vec
    robjects.globalenv["yvec"] = y_vec
    robjects.globalenv["labels"] = labels

    grdevices = importr('grDevices')
    importr('lattice')

    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=400,height=350)
    enforceTheme(robjects)

    rcmd="""
    print(
        xyplot(yvec~xvec,type=c('p','r'),
                ylab='%s',xlab='%s',
                auto.key=list(lines=T,points=T,corner=c(0,.9),background='white'),
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


def fetch_match_attributes(summaries,attribute):
    if attribute=='duration':
        vector_list = [summary.match.duration/60.0 for summary in summaries]
        label='Game length (m)'
    elif attribute=='K-D+.5*A':
        vector_list = [summary.kills - summary.deaths + summary.assists*.5 for summary in summaries]
        label='Kills - Death + .5*Assists'
    elif attribute == 'player':
        vector_list = [summary.player.persona_name for summary in summaries]
        label=attribute.title()
    elif attribute == 'is_win':
        vector_list = ['Won' if summary.is_win==True else 'Lost' for summary in summaries]
        label='Won Game?'
    elif attribute == 'game_mode':
        vector_list = [summary.match.game_mode.description for summary in summaries]
        label='Game Mode'
    elif attribute == 'skill':
        vector_list = [summary.match.skill for summary in summaries]
        label='Skill (3 = High)'
    elif attribute == 'hero_name':
        vector_list = [safen(summary.hero.name) for summary in summaries]
        label='Hero Name'
    else:
        vector_list = [getattr(summary, attribute) for summary in summaries]
        label=safen(attribute)


    return vector_list, label

