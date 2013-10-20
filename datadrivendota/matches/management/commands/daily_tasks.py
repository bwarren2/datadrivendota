from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from matches.models import PlayerMatchSummary, Match
from matches.management.tasks.valve_api_calls import RefreshUpdatePlayerPersonas, RefreshPlayerMatchDetail, ApiContext
class Command(BaseCommand):

    def handle(self, *args, **options):


        c = ApiContext()
        RefreshUpdatePlayerPersonas().delay(api_context=c)
#        c = ApiContext()
#        RefreshPlayerMatchDetail().delay(api_context=c)

        #Denoramlization Checks
        radiant_badness = PlayerMatchSummary.objects.filter(
            match__radiant_win=True,player_slot__lte=5,is_win=False)
        if len(radiant_badness) != 0:
            send_mail('Denormalization alert!',
                'We have denormalization for radiant players and iswin=False',
                'datadrivendota@gmail.com',['datadrivendota@gmail.com'],
                fail_silently=False)

        dire_badness = PlayerMatchSummary.objects.filter(match__radiant_win=True,
            player_slot__gte=5,is_win=True)
        if len(dire_badness) != 0:
            send_mail('Denormalization alert!',
                'We have denormalization for dire players and iswin=True',
                'datadrivendota@gmail.com',['datadrivendota@gmail.com'],
                fail_silently=False)

        matches = Match.objects.filter(duration__gte=settings.MIN_MATCH_LENGTH)
        matches.annotate(Count('playermatchsummary'))

        bad_matches = []
        for match in matches:
            if match.playermatchsummary__count<10:
                bad_matches.append(match)
            if match.playermatchsummary__count>10:
                bad_matches.append(match)


        send_mail('Denormalization alert!',
                    'We have incomplete matches! %s'%bad_matches,
                    'datadrivendota@gmail.com',['datadrivendota@gmail.com'],
                    fail_silently=False)


        #PlayerMatchSummary.objects.filter(player=player).values('hero__machine_name','is_win').annotate(Count('is_win'))
