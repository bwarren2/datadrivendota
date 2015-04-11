from rest_framework import serializers
from matches.models import Match, PlayerMatchSummary


class MatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Match
        fields = (
            'steam_id',
            'start_time',
            'duration',
            'radiant_win',
            'skill')


class PlayerMatchSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = PlayerMatchSummary
        fields = (
            'kills',
            'deaths',
            'assists',
            'last_hits',
            'denies',
            'gold',
            'gold_per_min',
            'xp_per_min',
            'hero_damage',
            'hero_healing',
            'tower_damage',
            'level',
            'is_win',
            'gold_total',
            'xp_total',
            'kda2',
            'side',
        )
