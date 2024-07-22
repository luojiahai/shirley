from rest_framework import serializers


class ChatSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1024)
