from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'gender', 'avatar', 'email', 'password', 'id')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return Client.objects.create_user(**validated_data)
