import datetime
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models import Count
from datadrivendota.utilities import error_email
from matches.models import PlayerMatchSummary, Match
from heroes.models import Hero, Role
from optparse import make_option


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '--full',
            action='store',
            dest='full_denorm_check',
            help='Are we doing absolutely errybody?',
        ),
    )

    def handle(self, *args, **options):
        full_check = options['full_denorm_check']
        #Everything that is too short is uncounted
        # .exclude(lobby_type__steam_id=7)

        def process_matches(unprocessed):
            def tournament(unprocessed):
                matches = unprocessed.filter(
                    skill=4
                )
                matches.update(validity=Match.LEGIT)

            def too_short(unprocessed):
                matches = unprocessed.filter(
                    duration__lte=settings.MIN_MATCH_LENGTH
                )
                matches.update(validity=Match.UNCOUNTED)

            # Games that do not have ten match summaries are uncounted.
            def player_count(unprocessed):
                ms = unprocessed.annotate(Count('playermatchsummary'))
                ms = ms.filter(playermatchsummary__count__lt=10)
                keys = ms.values_list('pk', flat=True)
                ms = unprocessed.filter(pk__in=keys)
                ms.update(validity=Match.UNCOUNTED)

            # Games against bots do not count.
            def human_players(unprocessed):
                ms = unprocessed.filter(human_players__lt=10)
                ms.update(validity=Match.UNCOUNTED)

            # Games with leavers do not count.
            def leavers(unprocessed):
                ms = unprocessed.filter(
                    playermatchsummary__leaver__steam_id__gt=1
                )
                ms.update(validity=Match.UNCOUNTED)

            # Games with leavers do not count.
            def game_mode_check(unprocessed):
                ms = unprocessed.exclude(
                    lobby_type__steam_id__in=[0, 2, 6, 7]
                )
                ms.update(validity=Match.UNCOUNTED)

            # Things with ten human players, longer than min length, where no
            # one left, in the right lobby types, count
            def legitimize(unprocessed):
                unprocessed.filter(skill=4).update(validity=Match.LEGIT)
                ms = unprocessed.exclude(
                    duration__lte=settings.MIN_MATCH_LENGTH
                )
                ms = ms.exclude(human_players__lt=10)
                ms = ms.exclude(playermatchsummary__leaver__steam_id__gt=1)
                ms = ms.filter(lobby_type__steam_id__in=[0, 2, 6, 7])
                sub_selection = ms.annotate(Count('playermatchsummary'))
                sub_selection = sub_selection.filter(
                    playermatchsummary__count__lt=10
                )
                keys = sub_selection.values_list('pk', flat=True)
                ms = ms.exclude(pk__in=keys)
                ms.update(validity=Match.LEGIT)

            tournament(unprocessed)
            too_short(unprocessed)
            player_count(unprocessed)
            human_players(unprocessed)
            leavers(unprocessed)
            game_mode_check(unprocessed)
            legitimize(unprocessed)

        if full_check is not None:
            print "Doing all"
            unprocessed = Match.objects.all()
            process_matches(unprocessed)

        else:
            unprocessed = Match.objects.filter(validity=Match.UNPROCESSED)
            process_matches(unprocessed)

            a = datetime.datetime.utcnow()-datetime.timedelta(days=3)
            unprocessed = Match.objects.filter(
                start_time__gte=a.strftime('%s')
            )
            process_matches(unprocessed)


        # Match Integrity Checks
        radiant_badness = PlayerMatchSummary.objects.filter(
            match__radiant_win=True,
            player_slot__lte=5,
            is_win=False
        )
        if len(radiant_badness) != 0:
            error_email(
                'Database alert!',
                'We have denormalization for radiant players and iswin=False'
            )

        dire_badness = PlayerMatchSummary.objects.filter(
            match__radiant_win=True,
            player_slot__gte=5,
            is_win=True
        )
        if len(dire_badness) != 0:
            error_email(
                'Database alert!',
                'We have denormalization for dire players and iswin=True'
            )

        thumbshot_badness = Role.objects.filter(
            thumbshot=''
        )
        if len(dire_badness) != 0:
            roles = ", ".join([r.name for r in thumbshot_badness])
            error_email(
                'Database alert!',
                'We have roles without thumbshots: {0}'.format(roles)
            )

        matches = Match.objects.filter(duration__gte=settings.MIN_MATCH_LENGTH)
        matches = matches.annotate(Count('playermatchsummary'))

        # pmses =PlayerMatchSummary.objects.filter(
        #     match__validity=Match.LEGIT,
        #     ).exclude(skill_build__level=1)
        bad_matches = []
        for match in matches:
            if match.playermatchsummary__count < 10:
                bad_matches.append(match)
            if match.playermatchsummary__count > 10:
                bad_matches.append(match)

        m = Match.objects.filter(steam_id=0)
        if len(m) != 0:
            error_email(
                'Database alert!',
                'We have a match with steam_id 0'
            )

        # Hero Integrity checks
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
            except ObjectDoesNotExist:
                error_msg += "%s is missing a dossier \n" % hero.name
        if error_msg != '':
            error_email('Database alert!', error_msg)
