from rest_framework import serializers
from .models import PingRequest


class PingRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = PingRequest
        exclude = ('id',)
