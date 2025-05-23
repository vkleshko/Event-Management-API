from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=True)
