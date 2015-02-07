from rest_framework import serializers
from .models import Team


class TeamSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, obj):
        try:
            return obj.logo_image.url
        except ValueError:
            return ''

    class Meta:
        model = Team
        fields = ('steam_id', 'name', 'tag', 'logo_url')
