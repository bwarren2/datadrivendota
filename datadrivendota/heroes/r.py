from uuid import uuid4

from django.core.files import File
#from django.conf import settings
from django.core.files.storage import default_storage

from rpy2 import robjects
from rpy2.robjects.packages import importr

from heroes.models import HeroDossier, Hero


def generateChart(hero_list, stats_list):
    # Currently, we are violating DRY with the available field listing from the form
    # and the R space being in different places and requiring that they are the same.

    grdevices = importr('grDevices')

    importr('lattice')
    selected_heroes = HeroDossier.objects.filter(hero__id__in=hero_list)

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
    imagefile = File(open('datadrivendota/media/1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    robjects.r("""print(
        xyplot(%s~level,groups=hero,data=df.all,type='l',
                auto.key=list(lines=T,points=F,space='right'),
                par.settings=simpleTheme(lwd=4,col=rainbow(n=length(unique(df.all$hero)))),
                ylab='Value',
                scales=list(y=list(relation='free'))
                )
    )""" % "+".join(stats_list))
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    return imagefile



    # This is a goofy hack.  I do not know why putting the plot between open
    # and write does not work here.
    #imagefile2 = open(imagefile.name, 'r')

    #Try making a new file and sending that to s3
    #s3file = default_storage.open('1d_%s.bmp' % str(uuid4()), 'w')
    #s3file.write(imagefile2.read())
    #s3file.close()
    #imagefile2.close()

    #return s3file

def lineupChart(heroes, stat, level):

    grdevices = importr('grDevices')
    importr('lattice')
    all_heroes = HeroDossier.objects.all()

    cmd = """
        df.all = data.frame(
            )
        """
    robjects.r(cmd)

    selected_heroes = Hero.objects.filter(id__in=heroes)

    for hero in all_heroes:

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
            day_vision=%s,
            night_vision=%s,
            atk_point=%s,
            atk_backswing=%s,
            turn_rate=%s,
            legs=%s,
            movespeed=%s,
            projectile_speed=%s,
            range=%s,
            base_atk_time=%s,
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
               hero.day_vision,
               hero.night_vision,
               hero.atk_point,
               hero.atk_backswing,
               hero.turn_rate,
               hero.legs,
               hero.movespeed,
               hero.projectile_speed,
               hero.range,
               hero.base_atk_time,
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
    hero_names = list()
    for hero in selected_heroes:
        hero_names.append(hero.safe_name())

    joinstr = "','".join(hero_names)

    robjects.r("df.all = cbind(df.all,df.thing)")

    cmd = "df.all = df.all[df.all$level==%s,]" %  level[0]
    cmd += "\n" +"df.all = df.all[order(-df.all$%s),]" % stat[0]
    cmd += "\n" +"df.all$hero = factor(x = df.all$hero, levels=unique(df.all$hero),ordered=T)"

    cmd += "\n" +"highlight_hero_vec = c('%s')" % joinstr

    cmd += "\n" +"colvec = ifelse(match(df.all$hero,highlight_hero_vec), 'red','green')"
    cmd += "\n" +"colvec = ifelse(is.na(colvec), 'green', 'red')"
    robjects.r(cmd)

    #Make a file
    imagefile = File(open('datadrivendota/media/1d_%s.png' % str(uuid4()), 'w'))
    grdevices.png(file=imagefile.name, type='cairo',width=850,height=500)
    robjects.r("""print(
        barchart({0}~hero,data=df.all,type='l',
                auto.key=list(lines=T,points=F,space='right'),
                par.settings=simpleTheme(lwd=2,),
                scales=list(y=list(relation='free'),x=list(rot=90)),
                col=colvec,
                ylab='Value',
                origin = 0
                )
    )""".format(stat[0]))
    #relation='free' in scales for independent axes
    grdevices.dev_off()
    imagefile.close()

    return imagefile

