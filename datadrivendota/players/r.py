from uuid import uuid4

from django.core.files import File
from django.db.models import Count
from rpy2 import robjects
from rpy2.robjects.packages import importr

from matches.models import PlayerMatchSummary
from .models import Player
from datadrivendota.r import s3File
from heroes.models import safen

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
    data_list.extend([summary.kills-summary.deaths+summary.assists/2 for summary in summaries])
    label_list.extend(['K-D+A/2'] * (len(data_list)-len(label_list)))

    x_vector = robjects.FloatVector(data_list)
    category_vector = robjects.StrVector(label_list)
    robjects.globalenv['cat_vec'] = category_vector
    robjects.globalenv['x_vec'] = x_vector

    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=600,height=500)
    robjects.r("""
    print(
        densityplot(~x_vec,groups=cat_vec,
                auto.key=list(lines=T,points=F,space='right'),
                par.settings=simpleTheme(lwd=2,),
        )
    )""")
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile)
    return hosted_file

def CountWinrate(player_id):
    grdevices = importr('grDevices')
    importr('lattice')

    player = Player.objects.get(steam_id=player_id)

    annotations = PlayerMatchSummary.objects.filter(player=player).values('hero__machine_name','is_win').annotate(Count('is_win'))
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
    robjects.r("""
    print(
        xyplot(win_rates~games,labels=labels,
                auto.key=list(lines=F,points=T,space='right'),
                par.settings=simpleTheme(lwd=2),
                ylab='Win %',
                xlab='Games Played',
                panel=function(x, y, ...) {
                  panel.xyplot(x, y, ...);
                  ltext(x=x, y=y, labels=labels, pos=1, offset=1, cex=0.8)
                  panel.abline(h=50,lty=3,col='darkgray')
                  panel.abline(v=10,lty=3,col='darkgray')
                }

        )
    )""")
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile)
    return hosted_file
