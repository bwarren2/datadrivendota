from rest_framework.routers import DefaultRouter
from matches.viewsets import (
    MatchViewSet,
    PlayerMatchSummaryViewSet,
    SkillBuildViewSet,
    MatchPickBanViewSet,
    PickBanViewSet,
)
from heroes.viewsets import (
    HeroViewSet,
    HeroDossierViewSet,
    HeroWinrateViewSet,
    HeroPickBanViewSet,
)
from items.viewsets import ItemViewSet
from teams.viewsets import TeamViewSet
from leagues.viewsets import LeagueViewSet
# from players.viewsets import PlayerViewSet
from players.viewsets import PlayerWinrateViewSet
from accounts.viewsets import PingRequestViewSet


# DRF is great
router = DefaultRouter()
router.register('teams', TeamViewSet)
router.register('leagues', LeagueViewSet)
router.register('heroes', HeroViewSet)
router.register('pickbans', PickBanViewSet)
router.register(
    'match-pickban',
    MatchPickBanViewSet,
    base_name='match-pickban'
)
router.register(
    'hero-winrate',
    HeroWinrateViewSet,
    base_name='hero-winrate'
)
router.register(
    'player-winrate',
    PlayerWinrateViewSet,
    base_name='player-winrate'
)
router.register(
    'hero-pickban',
    HeroPickBanViewSet,
    base_name='hero-pickban'
)
router.register('hero-dossiers', HeroDossierViewSet)
router.register('items', ItemViewSet)
router.register('matches', MatchViewSet)
router.register(
    'player-match-summary',
    PlayerMatchSummaryViewSet,
    base_name='player-match-summary'
)
router.register(
    'skillbuild',
    SkillBuildViewSet,
    base_name='skillbuild'
)
# router.register('players', PlayerViewSet)
router.register('ping-requests', PingRequestViewSet)
