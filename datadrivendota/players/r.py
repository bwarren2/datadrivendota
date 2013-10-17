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

def CountWinrate(player_id, min_date=datetime.date(2009,1,1), max_date=None):
    if max_date==None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    min_dt_utc = mktime(min_date.timetuple())

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

def PlayerTimeline(player_id, min_date, max_date, bucket_var, plot_var):

    grdevices = importr('grDevices')
    importr('lattice')

    if max_date==None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    min_dt_utc = mktime(min_date.timetuple())
    player = Player.objects.get(steam_id=player_id)
    pms = PlayerMatchSummary.objects.filter(player=player).select_related()
    pms = pms.filter()
    pms = pms.filter(match__duration__gte=settings.MIN_MATCH_LENGTH)
    pms = pms.filter(match__start_time__gte=min_dt_utc)
    pms = pms.filter(match__start_time__lte=max_date_utc)

    wins = [1 if m.is_win else 0 for m in pms]
    start_times = [m.match.start_time for m in pms]

    wins_vec = robjects.IntVector(wins)
    start_times_vec = robjects.IntVector(start_times)

    robjects.globalenv['wins_vec']=wins_vec
    robjects.globalenv['start_times_vec']=start_times_vec

    if plot_var == 'winrate':
        plot_func = 'winrate'
    else:
        plot_func = 'length'
    optionsDict = { 'date':
                        {'collapse_dt_format':r'%Y-%m-%d',
                         'present_dt_format':r'%Y-%m-%d'},
                    'hour_of_day':
                        {'collapse_dt_format':r'%H',
                         'present_dt_format':r'%Y-%m-%d'},
                    'month':
                        {'collapse_dt_format':r'%Y-%m',
                         'present_dt_format':r'%Y-%m-%d'},
                    'week':
                        {'collapse_dt_format':r'%Y-%W',
                         'present_dt_format':r'%Y-%m-%d'},}

    if bucket_var == 'hour_of_day':
        cmd = """
            collapse_date_format = '%s'
            local_timezone ='America/New_York'
            winrate = function(x){
                return(sum(x)/length(x));
            }

            df.spine=data.frame('x_spine'=seq(1,24),render_x=seq(1,24))

            xscale.components.A <- function(...) {
                # get default axes definition list; print user.value
                ans <- xscale.components.default(...)

                # - bottom labels
                ans$bottom$labels$labels <- df.spine$render_x
                ans$bottom$labels$at <- seq(0,length(ans$bottom$labels$labels),by=1)

                # return axes definition list
                return(ans)
            }


            time_var = format(as.POSIXct(start_times_vec, origin="1970-01-01", tz="GMT"),tz=local_timezone,collapse_date_format)
            df.agg = aggregate(x=wins_vec,by=list(time_var),FUN=%s)
            colnames(df.agg) = c('group','var')
            df.plot2 = merge(x=df.spine,y=df.agg,all.x=T,by.x='x_spine',by.y='group')
            df.plot2[is.na(df.plot2$var),'var']=0

            """ % (optionsDict[bucket_var]['collapse_dt_format'], plot_func)
    else:
        cmd = """

            winrate = function(x){
                return(sum(x)/length(x));
            }

            collapse_date_format = '%s'
            present_date_format = '%s'

            start_dt = min( format(as.POSIXct(start_times_vec, origin="1970-01-01", tz="GMT"),'%%Y-%%m-%%d') )
            end_dt = max( format(as.POSIXct(start_times_vec, origin="1970-01-01", tz="GMT"),'%%Y-%%m-%%d') )
            local_timezone ='America/New_York'
            days = seq(as.Date(start_dt), as.Date(end_dt), by="1 day")
            spine_psx_days = as.POSIXct(strptime(as.character(days), '%%Y-%%m-%%d'), origin="1970-01-01", tz=local_timezone)

            df.match = data.frame('present_dts'=format(spine_psx_days,present_date_format),'collapse_dts'=format(spine_psx_days,collapse_date_format))

            spine_x_vec = unique(format(spine_psx_days,collapse_date_format))
            df.spine =data.frame(x_spine=as.character(spine_x_vec))
            df.spine$x_spine= as.character(df.spine$x_spine)
            df.spine$render_x= df.match[match(x=df.spine$x_spine,table=df.match$collapse_dts),'present_dts']


            time_var = format(as.POSIXct(start_times_vec, origin="1970-01-01", tz="GMT"),tz=local_timezone,collapse_date_format)
            df.agg = aggregate(x=wins_vec,by=list(time_var),FUN=%s)
            colnames(df.agg) = c('group','var')
            df.plot2 = merge(x=df.spine,y=df.agg,all.x=T,by.x='x_spine',by.y='group')
            df.plot2[is.na(df.plot2$var),'var']=0

            if(length(df.plot2$render_x)>40){
                sq = seq(1,length(df.spine$render_x),1)
                d = ifelse(sq%%%%(round(length(df.spine$render_x)/25,0))==1,as.character(df.spine$render_x),'');
            }
            xscale.components.A <- function(...) {
                # get default axes definition list; print user.value
                ans <- xscale.components.default(...)

                # - bottom labels
                ans$bottom$labels$labels <- d
                ans$bottom$labels$at <- seq(1,length(ans$bottom$labels$labels),by=1)
                # return axes definition list
                return(ans)
            }
            """ % (optionsDict[bucket_var]['collapse_dt_format'], optionsDict[bucket_var]['present_dt_format'], plot_func)
    robjects.r(cmd)

    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo', width=800,height=500)

    enforceTheme(robjects)
    if plot_var == 'winrate':
        cmd = """
            print(
                 barchart(var~render_x,data=df.plot2,type='h',horizontal=F,
                    scales=list(x=list(rot=90)),col='purple',
                    origin=0,xlab='%s',ylab='%s',
                    panel=function(x, y, ...) {
                      panel.barchart(x, y, ...);
                      panel.abline(h=.5,lty=3,col='blue')
                    }, ylim=c(0,1),
                    xscale.components=xscale.components.A

                )
            )
        """ % (bucket_var.replace("_"," ").title(),plot_var.replace("_"," ").title())
    else:
            cmd = """
        print(
             barchart(var~render_x,data=df.plot2,type='h',horizontal=F,
                scales=list(x=list(rot=90)),col='purple',
                origin=0,xlab='%s',ylab='%s',
                xscale.components=xscale.components.A
            )
        )
    """ % (bucket_var.replace("_"," ").title(),plot_var.replace("_"," ").title())

    #
    robjects.r(cmd)
    grdevices.dev_off()
    imagefile.close()



    hosted_file = s3File(imagefile)
    print imagefile, hosted_file
    return hosted_file
