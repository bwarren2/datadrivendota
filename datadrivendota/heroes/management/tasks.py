from celery import chain, Task
from copy import deepcopy
import logging
from django.conf import settings
from datadrivendota.utilities import error_email
from datadrivendota.management.tasks import (
    ValveApiCall,
    ApiContext,
)
from heroes.models import Hero, Role, HeroDossier
from matches.management.tasks import CycleApiCall

logger = logging.getLogger(__name__)


class MirrorHeroSkillData(Task):
    """
    Gets skill-level games for a given hero from Valve.
    """

    def run(self):
        heroes = Hero.objects.all()
        for hero in heroes:

            for skill in [1, 2, 3]:

                c = ApiContext()
                c.matches_requested = settings.HERO_SKILL_MATCH_COUNT
                c.matches_desired = settings.HERO_SKILL_MATCH_COUNT
                c.hero_id = hero.steam_id
                c.deepcopy = False
                c.skill = skill
                vac = ValveApiCall()
                rpr = CycleApiCall()
                pass_context = deepcopy(c)
                chain(vac.s(
                    mode='GetMatchHistory',
                    api_context=pass_context
                ), rpr.s()).delay()

        logger.info("Finished kicking off hero skill data")


class CheckHeroIntegrity(Task):
    """
    Checks that we have the things we expect to for hero-models.
    """

    def run(self):
        thumbshot_badness = Role.objects.filter(
            thumbshot=''
        )
        if len(thumbshot_badness) != 0:
            roles = ", ".join([r.name for r in thumbshot_badness])
            error_email(
                'Database alert!',
                'We have roles without thumbshots: {0}'.format(roles)
            )

        h = Hero.objects.filter(thumbshot='').exclude(visible=False)
        if len(h) != 0:
            error_email(
                'Database alert!',
                'We have a hero without a thumbshot url'
            )

        h = Hero.objects.filter(name='').exclude(visible=False)
        if len(h) != 0:
            error_email(
                'Database alert!',
                'We have a hero without a name'
            )

        heroes = Hero.objects.all().exclude(visible=False)
        error_msg = ''
        for hero in heroes:
            try:
                hero.herodossier
            except HeroDossier.DoesNotExist:
                error_msg += "%s is missing a dossier \n" % hero.name
        if error_msg != '':
            error_email('Database alert!', error_msg)
