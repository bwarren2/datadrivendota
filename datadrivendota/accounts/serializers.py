from rest_framework import serializers
from .models import MatchRequest


class MatchRequestSerializer(serializers.ModelSerializer):
    match_id = serializers.IntegerField()

    class Meta:

        model = MatchRequest
        fields = ('match_id',)
