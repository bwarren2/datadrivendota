from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Count
from datadrivendota.utilities import error_email
from matches.models import PlayerMatchSummary, Match
from heroes.models import Hero
class Command(BaseCommand):

    def handle(self, *args, **options):



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
        matches.annotate(Count('playermatchsummary'))

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
        h = Hero.objects.filter(steam_id=0)
        if len(h)!=0:
            error_email('Database alert!',
                'We have an invalid hero with steam_id 0')

        h = Hero.objects.filter(thumbshot_url='')
        if len(h)!=0:
            error_email('Database alert!',
                'We have a hero without a thumbshot url')

        heroes = Hero.objects.all()
        error_msg = ''
        for hero in heroes:
            try:
                hero.herodossier
            except Hero.DoesNotExist:
                error_msg+="%s is missing a dossier \n" % hero.name
        if error_msg!='':
            error_email('Database alert!',error_msg)

        #PMS integrity checks
        pms = PlayerMatchSummary.objects.filter(hero_steam_id=0)
        if len(pms)!=0:
            error_email('Database alert!',
                'We have a playermatchsummary that uses the 0 hero.')


        #PlayerMatchSummary.objects.filter(player=player).values('hero__machine_name','is_win').annotate(Count('is_win'))

