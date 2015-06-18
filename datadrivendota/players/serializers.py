from rest_framework import serializers
from players.models import Player


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        fields = ('steam_id', 'persona_name', 'pro_name', 'avatar', )


class PlayerWinrateSerializer(serializers.Serializer):
    player = serializers.SerializerMethodField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    games = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super(PlayerWinrateSerializer, self).__init__(*args, **kwargs)
        self.pros = {p.steam_id: p for p in Player.pros.all()}

    def get_player(self, obj):
        try:
            return PlayerSerializer(self.pros[obj['player__steam_id']]).data
        except AttributeError:
            return ''

    class Meta:
        fields = (
            'player',
            'wins',
            'losses',
            'games',
        )
