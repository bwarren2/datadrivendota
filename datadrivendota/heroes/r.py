from heroes.models import HeroDossier
from rpy2 import robjects
#from rpy2 import rinterface
from rpy2.robjects.packages import importr
from django.core.files import File
from django.conf import settings


def generateChart(hero_name_list, stats_list):
    # Currently, we are violating DRY with the available field listing from the form
    # and the R space being in different places and requiring that they are the same.

    grdevices = importr('grDevices')

    importr('lattice')
    selected_heroes = HeroDossier.objects.filter(hero__name__in=hero_name_list)

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
               hero.hero.machine_name)
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
    imagefile = File(open(settings.MEDIA_ROOT+'/temp/file2.png', 'w'))
    grdevices.png(file=imagefile.name)
    robjects.r("""print(
        xyplot(%s~level,groups=hero,data=df.all,type='l',
                auto.key=T,pch=2,cex=3,lwd=4,scales=list(y=list(relation='free'))
                )
    )""" % "+".join(stats_list))
    #relation='free' in scales for independent axes
    grdevices.dev_off()

    return imagefile
