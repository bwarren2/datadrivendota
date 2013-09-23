from uuid import uuid4
import datetime
from time import mktime
from django.core.files import File
from django.db.models import Count
from rpy2 import robjects
from rpy2.robjects.packages import importr

from matches.models import PlayerMatchSummary, GameMode
from .models import Player
from datadrivendota.r import s3File, enforceTheme
from heroes.models import safen
from django.conf import settings


def KDADensity(player_id):

    grdevices = importr('grDevices')
    importr('lattice')

    player = Player.objects.get(steam_id=player_id)

    summaries = PlayerMatchSummary.objects.filter(player=player)


    data_list = [summary.kills for summary in summaries]
    label_list = ['kills'] * len(data_list)

    data_list.extend([summary.deaths for summary in summaries])
    label_list.extend(['deaths'] * (len(data_list)-len(label_list)))

    data_list.extend([summary.assists for summary in summaries])
    label_list.extend(['assists'] * (len(data_list)-len(label_list)))

    KDA2 = [summary.kills-summary.deaths+summary.assists/2 for summary in summaries]
    data_list.extend(KDA2)
    label_list.extend(['K-D+A/2'] * (len(data_list)-len(label_list)))

    x_vector = robjects.FloatVector(data_list)
    category_vector = robjects.StrVector(label_list)
    robjects.globalenv['cat_vec'] = category_vector
    robjects.globalenv['x_vec'] = x_vector
    robjects.globalenv['KDA2_median'] = sorted(KDA2)[int(len(KDA2)/2.0)]

    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=600,height=500)
    enforceTheme(robjects)

    robjects.r("""
    print(
        densityplot(~x_vec,groups=cat_vec,
                xlab='',
                panel=function(x,...){
                    panel.densityplot(x,...);
                    panel.abline(v=KDA2_median)
                },
                auto.key= list(lines=T,points=F,
                    corner=c(0,.99),background='white')
        )
    )""")
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile)
    return hosted_file

def CountWinrate(player_id, min_date='2009-01-01', max_date=None, game_mode_list='Competitive' ):

    if max_date==None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(datetime.datetime.strptime(max_date,"%Y-%m-%d").timetuple())

    min_dt_utc = mktime(datetime.datetime.strptime(min_date,"%Y-%m-%d").timetuple())

    if game_mode_list=='Competitive':
        game_mode_list = GameMode.objects.filter(is_competitive=True)
    else:
        game_mode_list = GameMode.objects.filter(steam_id__in=game_mode_list)
    grdevices = importr('grDevices')
    importr('lattice')

    player = Player.objects.get(steam_id=player_id)
    annotations = PlayerMatchSummary.objects.filter(player=player).values('hero__machine_name','is_win').annotate(Count('is_win'))
    annotations = annotations.filter(match__duration__gte=settings.MIN_MATCH_LENGTH)
    annotations = annotations.filter(match__start_time__gte=min_dt_utc)
    annotations = annotations.filter(match__start_time__lte=max_date_utc)
    annotations = annotations.filter(match__game_mode__in=game_mode_list)


    heroes = list(set([row['hero__machine_name'] for row in annotations]))
    wins = {row['hero__machine_name']: row['is_win__count'] for row in annotations if row['is_win']==True}
    losses = {row['hero__machine_name']: row['is_win__count'] for row in annotations if row['is_win']==False}

    win_rates = robjects.FloatVector([float(wins.get(hero,0))/(wins.get(hero,0)+losses.get(hero,0))*100 for hero in heroes])
    games = robjects.IntVector([wins.get(hero,0)+losses.get(hero,0) for hero in heroes])
    labels = robjects.StrVector([safen(hero) for hero in heroes])

    robjects.globalenv['labels'] = labels
    robjects.globalenv['win_rates'] = win_rates
    robjects.globalenv['games'] = games


    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=500,height=500)

    enforceTheme(robjects)
    cmd = """
    print(
        xyplot(win_rates~games,labels=labels,
                auto.key=list(lines=F,points=T,corner=c(0,.9)),
                ylab='Win %',
                xlab='Games Played',
                panel=function(x, y, ...) {
                  panel.xyplot(x, y, ...);
                  ltext(x=x, y=y, labels=labels, pos=1, offset=.1, cex=0.8)
                  panel.abline(h=50,lty=3,col='blue')
                  panel.lines(x=seq(0,100,1),y=100*(.5+(1/(2*sqrt(seq(0,100,1))))),lty=3,col='darkgray')
                  panel.lines(x=seq(0,100,1),y=100*(.5-(1/(2*sqrt(seq(0,100,1))))),lty=3,col='darkgray')
                  panel.lines(x=seq(0,100,1),y=100*(.5+2*(1/(2*sqrt(seq(0,100,1))))),lty=3,col='red')
                  panel.lines(x=seq(0,100,1),y=100*(.5-2*(1/(2*sqrt(seq(0,100,1))))),lty=3,col='red')

                  panel.abline(v=10,lty=3,col='blue')
                },

        )
    )"""
    robjects.r(cmd)
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile)
    return hosted_file
