from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = (
            'steam_id', 'thumbshot_url',
            'mugshot_url', 'internal_name',
            'name', 'cost'
        )
