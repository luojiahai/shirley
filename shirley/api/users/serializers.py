from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)
    password_repeated = serializers.CharField(max_length=128)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeated']:
            raise serializers.ValidationError('passwords do not match!')
        return attrs
