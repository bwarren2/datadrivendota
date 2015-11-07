from rest_framework import serializers
from .models import MatchRequest, PingRequest


class MatchRequestSerializer(serializers.ModelSerializer):
    match_id = serializers.IntegerField()

    class Meta:
        model = MatchRequest
        fields = ('match_id',)


class PingRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PingRequest
        exclude = ('id',)
