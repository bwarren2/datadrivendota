from uuid import uuid4
from django.core.files import File
from django.core.files.storage import default_storage
from rpy2 import robjects
from rpy2.robjects import Formula, FloatVector, StrVector
from rpy2.robjects.packages import importr
from matches.models import PlayerMatchSummary
from steamusers.models import SteamUser


def EndgameChart(player_list,x_var,y_var,split_var,group_var):


    player_obj_list = []
    for id in player_list:
        player_obj_list.append(SteamUser.objects.get(steam_id=id))

    grdevices = importr('grDevices')

    #rprint = robjects.globalenv.get("print")

    lattice = importr('lattice')

    selected_summaries = PlayerMatchSummary.objects.select_related().filter(steam_user__in=player_obj_list)

    cmd = """
        df.all = data.frame(
            )
        """
    robjects.r(cmd)

    if x_var[0]=='duration':
        x_vector_list = [summary.match.duration/60.0 for summary in selected_summaries]
        #60 seconds in a minute
        xlab='Game length (m)'
    else:
        x_vector_list = [getattr(summary, x_var[0]) for summary in selected_summaries]
        xlab=x_var[0]


    if y_var[0]=='K-D+.5*A':
        y_vector_list = [summary.kills - summary.deaths + summary.assists*.5 for summary in selected_summaries]
        ylab='Kills - Death + .5*Assists'

    else:
        y_vector_list = [getattr(summary, y_var[0]) for summary in selected_summaries]
        ylab=y_var[0]


    x_vec = FloatVector(x_vector_list)
    y_vec = FloatVector(y_vector_list)


    if split_var[0] == 'player':
        split_vector_list = [summary.steam_user.steam_id for summary in selected_summaries]
    elif split_var[0] == 'is_win':
        split_vector_list = [summary.is_win for summary in selected_summaries]
    else:
        split_vector_list = [summary.match.game_mode.description for summary in selected_summaries]

    if group_var[0] == 'player':
        group_vector_list = [summary.steam_user.steam_id for summary in selected_summaries]
    elif group_var[0] == 'is_win':
        group_vector_list = [summary.is_win for summary in selected_summaries]
    else:
        group_vector_list = [summary.match.game_mode.description for summary in selected_summaries]
    grouplab=group_var[0]


    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    """
    formula = Formula('yvec ~ xvec | splitvar')
    formula.getenvironment()['yvec'] = y_vec
    formula.getenvironment()['xvec'] = x_vec
    formula.getenvironment()['splitvar'] = StrVector(split_vector_list)
    p = lattice.xyplot(formula,xlab=xlab,ylab=ylab,groups=group_vector_list)
"""
    robjects.globalenv["xvec"] = x_vec
    robjects.globalenv["yvec"] = y_vec
    robjects.globalenv["splitvar"] = StrVector(split_vector_list)
    robjects.globalenv["groupvar"] = StrVector(group_vector_list)

    rcmd="""print(
        xyplot(yvec~xvec|splitvar,groups=groupvar,type=c('p','r'),
                auto.key=list(rectangles=F,points=T,lines=T,space='right',title='%s'),
                ylab='%s',xlab='%s',
                par.settings=simpleTheme(pch=20,lwd=4,
                    col=rainbow(n=length(unique(groupvar))),
                    ),
                scales=list(y=list(relation='free'))
                )
    )"""% (grouplab, ylab, xlab)
    print rcmd
    robjects.r(rcmd )


    grdevices.dev_off()

    imagefile.close()

    # This is a goofy hack.  I do not know why putting the plot between open
    # and write does not work here.
    imagefile2 = open(imagefile.name, 'r')

    #Try making a new file and sending that to s3
    s3file = default_storage.open('1d_%s.bmp' % str(uuid4()), 'w')
    s3file.write(imagefile2.read())
    s3file.close()
    imagefile2.close()

    return s3file


