from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Count
from datadrivendota.utilities import error_email
from matches.models import PlayerMatchSummary, Match
from heroes.models import Hero
class Command(BaseCommand):

    def handle(self, *args, **options):


        #Fix Matches
        matches = Match.objects.filter(duration__lte=settings.MIN_MATCH_LENGTH)
        matches.update(validity=Match.UNCOUNTED)

        #Games that do not have ten match summaries are uncounted, but we need to re-check things in the scrape.
        unprocessed = Match.objects.filter(validity=Match.UNPROCESSED)
        ms = unprocessed.annotate(Count('playermatchsummary'))
        ms = ms.filter(playermatchsummary__count__lt=10)
        keys = ms.values_list('pk', flat=True)
        ms = unprocessed.filter(pk__in=keys)
        ms.update(validity=Match.UNCOUNTED)

        #Games against bots do not count.
        ms = unprocessed.filter(human_players__lt=10)
        ms.update(validity=Match.UNCOUNTED)

        #Games with leavers do not count.
        ms = unprocessed.filter(playermatchsummary__leaver__steam_id__gt=1)
        ms.update(validity=Match.UNCOUNTED)

        #Things with ten human players, longer than min length, where no one left count
        ms = unprocessed.exclude(duration__lte=settings.MIN_MATCH_LENGTH)
        ms = ms.exclude(human_players__lt=10)
        ms = ms.exclude(playermatchsummary__leaver__steam_id__gt=1)
        sub_selection = ms.annotate(Count('playermatchsummary'))
        sub_selection = sub_selection.filter(playermatchsummary__count__lt=10)
        keys = sub_selection.values_list('pk', flat=True)
        ms = unprocessed.exclude(pk__in=keys)
        ms.update(validity=Match.LEGIT)



        #Match Integrity Checks
        radiant_badness = PlayerMatchSummary.objects.filter(
            match__radiant_win=True,player_slot__lte=5,is_win=False)
        if len(radiant_badness) != 0:
            error_email('Database alert!',
                'We have denormalization for radiant players and iswin=False')


        dire_badness = PlayerMatchSummary.objects.filter(match__radiant_win=True,
            player_slot__gte=5,is_win=True)
        if len(dire_badness) != 0:
            error_email('Database alert!',
                'We have denormalization for dire players and iswin=True')

        matches = Match.objects.filter(duration__gte=settings.MIN_MATCH_LENGTH)
        matches = matches.annotate(Count('playermatchsummary'))

        bad_matches = []
        for match in matches:
            if match.playermatchsummary__count<10:
                bad_matches.append(match)
            if match.playermatchsummary__count>10:
                bad_matches.append(match)

        m = Match.objects.filter(steam_id=0)
        if len(m)!=0:
            error_email('Database alert!',
                'We have a match with steam_id 0')



        #Hero Integrity checks
        h = Hero.objects.filter(thumbshot='')
        if len(h)!=0:
            error_email('Database alert!',
                'We have a hero without a thumbshot url')

        h = Hero.objects.filter(name='')
        if len(h)!=0:
            error_email('Database alert!',
                'We have a hero without a name')

        heroes = Hero.objects.all()
        error_msg = ''
        for hero in heroes:
            try:
                hero.herodossier
            except ObjectDoesNotExist:
                error_msg+="%s is missing a dossier \n" % hero.name
        if error_msg!='':
            error_email('Database alert!',error_msg)

