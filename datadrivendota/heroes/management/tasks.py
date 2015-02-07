from celery import chain
from copy import deepcopy
import logging
from datadrivendota.management.tasks import (
    BaseTask,
    ValveApiCall,
)
from matches.management.tasks import CycleApiCall

logger = logging.getLogger(__name__)


class MirrorHeroSkillData(BaseTask):
    """
    Hets skill-level games for a given hero from Valve.
    """

    def run(self):

        if self.valid_context():

            self.fill_default_context()

            for skill in self.api_context.skill_levels:

                self.api_context.skill = skill
                vac = ValveApiCall()
                rpr = CycleApiCall()
                pass_context = deepcopy(self.api_context)
                chain(vac.s(
                    mode='GetMatchHistory',
                    api_context=pass_context
                ), rpr.s()).delay()

            logger.info("Finished kicking off hero skill data")
        else:
            logger.error(
                "Not allowed to have an account_id for this, and need a Hero."
            )
            raise ValueError(
                "Not allowed to have an account_id for this, and need a Hero."
                )

    def valid_context(self):
        if (
            self.api_context.account_id is not None
            or self.api_context.hero_id is None
        ):
            return False
        else:
            return True

    def fill_default_context(self):
        if self.api_context.matches_requested is None:
            self.api_context.matches_requested = 100

        self.api_context.deepcopy = False

        if self.api_context.matches_desired is None:
            self.api_context.matches_desired = 100

        self.api_context.skill_levels = [1, 2, 3]
