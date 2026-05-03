from rest_framework import serializers
from db.models import Session, Streamer, Message

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
class StreamerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streamer
        fields = '__all__'
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'