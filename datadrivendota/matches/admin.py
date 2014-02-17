from django.contrib import admin

from matches.models import (
    Match,
    LobbyType,
    GameMode,
    LeaverStatus,
    SkillBuild,
    PlayerMatchSummary
)


admin.site.register(Match)
admin.site.register(LobbyType)
admin.site.register(GameMode)
admin.site.register(LeaverStatus)
admin.site.register(SkillBuild)
admin.site.register(PlayerMatchSummary)
