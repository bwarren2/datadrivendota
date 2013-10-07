from uuid import uuid4

from itertools import chain

from django.core.files import File
#from django.conf import settings

from rpy2 import robjects
from rpy2.robjects import FloatVector, StrVector
from rpy2.robjects.packages import importr

from heroes.models import HeroDossier, Hero
from datadrivendota.r import s3File, enforceTheme
from matches.models import PlayerMatchSummary
from matches.r import fetch_match_attributes
def generateChart(hero_list, stats_list, display_options):
    # Currently, we are violating DRY with the available field listing from the form
    # and the R space being in different places and requiring that they are the same.

    grdevices = importr('grDevices')

    importr('lattice')
    selected_heroes = HeroDossier.objects.filter(hero__name__in=hero_list)

    cmd = """
        df.all = data.frame(
            )
        """
    robjects.r(cmd)

    # Convention: Raw numbers that need to be modified to be right (like base
    # hero hp, which is always 150 at last check but gets gains from str, are
    # dubbed "base_".  A number inclusive of gains from stat growth is prefixless.
    # Modifiers (from stat points or items, w/e) will go into a "modified_"
    # variable, and final values (for plotting) are "final_")
    # NOTE: this convention is wrong with the numbers being imported as level 1
    # right now.
    for hero in selected_heroes:


        cmd = """
        df.all = rbind(df.all,
            data.frame(
            level=seq(1,25,1),
            strength=(seq(0,24,1)*%f)+%f,
            agility=(seq(0,24,1)*%f)+%f,
            intelligence=(seq(0,24,1)*%f)+%f,
            base_armor=rep(%f,25),
            base_hp=rep(%f,25),
            base_mana=rep(%f,25),
            base_hp_regen=rep(%f,25),
            base_mana_regen=rep(%f,25),
            base_dmg=rep(%f,25),
            agility_gain=seq(0,24,1)*%f,
            hero='%s'
            )
        )
        """ % (hero.strength_gain, hero.strength,
               hero.agility_gain, hero.agility,
               hero.intelligence_gain, hero.intelligence,
               hero.armor,
               hero.hp,
               hero.mana,
               hero.hp_regen,
               hero.mana_regen,
               (hero.max_dmg+hero.min_dmg)/2.0,
               hero.agility_gain,
               hero.hero.safe_name())
    #    print cmd
        robjects.r(cmd)
    cmd = """
        df.thing = data.frame(modified_armor = df.all$base_armor+df.all$agility_gain/7,
            hp=df.all$base_hp+df.all$strength*19,
            effective_hp = (1+0.06*(df.all$base_armor+df.all$agility_gain/7))*(df.all$base_hp+df.all$strength*19),
            mana=df.all$base_mana+df.all$intelligence*13
        )
        """
    #print cmd
    robjects.r(cmd)
    robjects.r("df.all = cbind(df.all,df.thing)")

    #Make a file
    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    enforceTheme(robjects)
    cmd="""print(
        xyplot(%s~level,groups=hero,data=df.all,type='l',
                auto.key=list(lines=T,points=F,corner=c(0,.9),background='white'),
                par.settings=simpleTheme(lwd=4,col=rainbow(n=length(unique(df.all$hero)))),
                ylab='Value',
                scales=list(y=list(%s))
                )
    )""" % ("+".join(stats_list),display_options['linked_scales'])
    robjects.r(cmd)
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile)
    return hosted_file


def lineupChart(heroes, stat, level):

    stat = stat[0]
    level = int(level[0])
    #Get the right stuff loaded in R
    grdevices = importr('grDevices')
    importr('lattice')

    #Database pulls and format python objects to go to R
    all_heroes = HeroDossier.objects.all().select_related()
    selected_heroes = Hero.objects.filter(name__in=heroes)
    selected_names = [hero.safe_name() for hero in selected_heroes]

    hero_value = dict((dossier.hero.safe_name(), fetch_value(dossier, stat, level)) for dossier in all_heroes)
    x_vals = [key for key in sorted(hero_value, key=hero_value.get, reverse=True)]
    y_vals = [hero_value[key] for key in sorted(hero_value, key=hero_value.get, reverse=True)]
    col_vec = ['red' if name in selected_names else 'green' for name in x_vals ]

    x = robjects.FactorVector(x_vals)
    y = robjects.FloatVector(y_vals)
    colors = robjects.StrVector(col_vec)
    df = robjects.DataFrame({'name':x, 'val':y})

    #Register in the environment

    robjects.globalenv["y"] = y
    robjects.globalenv["x"] = x
    robjects.globalenv["colors"] = colors
    robjects.globalenv["df"] = df


    #Some in-R formatting
    robjects.r("y = factor(y, levels = unique(y), ordered=T)")
    robjects.r("df$name = factor(df$name, levels = unique(df$name), ordered=T)")

    #Make a file
    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    enforceTheme(robjects)
    robjects.r("""print(
        barchart(val~name,data=df,type='l',horizontal=F,
                auto.key=list(lines=T,points=F,corner=c(0,.9),background='white'),
                par.settings=simpleTheme(lwd=2,),
                scales=list(y=list(relation='free'),x=list(rot=90)),
                ylab='%s',
                col=colors,
                origin = 0
                )
    )""" % stat.title())
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile)
    print imagefile, hosted_file
    return hosted_file

def HeroPerformanceChart(hero, player, game_mode_list, x_var, y_var, group_var, split_var):

    #Get the right stuff loaded in R
    grdevices = importr('grDevices')
    importr('lattice')

    #Database pulls and format python objects to go to R
    matches = PlayerMatchSummary.objects.filter(match__game_mode__in=game_mode_list)
    matches = matches.filter(hero__steam_id=hero)
    skill1 = matches.filter(match__skill=1)[:30]
    skill2 = matches.filter(match__skill=2)[:30]
    skill3 = matches.filter(match__skill=3)[:30]

    match_pool = list(chain(skill1, skill2, skill3))

    x_vector_list, xlab = fetch_match_attributes(match_pool, x_var)
    y_vector_list, ylab = fetch_match_attributes(match_pool, y_var)
    split_vector_list, split_lab = fetch_match_attributes(match_pool, split_var)
    group_vector_list, grouplab = fetch_match_attributes(match_pool, group_var)

    #Register in the environment
    x_vec = FloatVector(x_vector_list)
    y_vec = FloatVector(y_vector_list)

    robjects.globalenv["xvec"] = x_vec
    robjects.globalenv["yvec"] = y_vec
    robjects.globalenv["splitvar"] = StrVector(split_vector_list)
    robjects.globalenv["groupvar"] = StrVector(group_vector_list)

    #robjects.globalenv["y"] = y
    #Some in-R formatting

    #Make a file
    imagefile = File(open('1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    enforceTheme(robjects)
    rcmd="""print(
        xyplot(yvec~xvec|splitvar,groups=groupvar,type=c('p','r'),
                ylab='%s',xlab='%s',
                auto.key=list(lines=T,points=T,corner=c(0,.9),background='white',
                    title='%s',cex=.8),
                par.settings=simpleTheme(lwd=2,pch=20)
                )
    )"""% (ylab, xlab, grouplab)
    robjects.r(rcmd )
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    hosted_file = s3File(imagefile)
    print imagefile, hosted_file
    return hosted_file



def fetch_value(dossier, stat, level):

    easy_list = ['day_vision','night_vision','atk_point',
                 'atk_backswing','turn_rate','legs','movespeed',
                 'projectile_speed',
                 'range','base_atk_time']

    if hasattr(dossier, stat) and stat in easy_list:
        return getattr(dossier, stat)
    elif stat == "strength":
        return dossier.strength+(level-1)*dossier.strength_gain
    elif stat == "intelligence":
        return dossier.intelligence+(level-1)*dossier.intelligence_gain
    elif stat == "agility":
        return dossier.agility+(level-1)*dossier.agility_gain
    elif stat == "modified_armor":
        return dossier.armor + (dossier.agility+(level-1)*dossier.agility_gain)/7.0
    elif stat == "effective_hp":
        armor = dossier.armor + (dossier.agility+(level-1)*dossier.agility_gain)/7.0
        strength = dossier.strength+(level-1)*dossier.strength_gain
        hp = dossier.hp + strength*19
        return (1+0.06*armor) * hp
    elif stat == 'hp':
        strength = dossier.strength+(level-1)*dossier.strength_gain
        hp = dossier.hp + strength*19
        return hp
    elif stat == 'mana':
        intelligence = dossier.intelligence+(level-1)*dossier.intelligence_gain
        mana = dossier.mana + intelligence*13
        return mana
    else:
        raise KeyError("What is %s" % stat)
