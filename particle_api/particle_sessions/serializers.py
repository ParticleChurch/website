from rest_framework import serializers
from particle_api.helpers import TimestampField

from particle_sessions.models import *

class ParticleSessionSerializer(serializers.ModelSerializer):
    time_opened = TimestampField()
    time_last_seen = TimestampField()
    time_closed = TimestampField()
    
    class Meta:
        model = ParticleSession
        fields = [
            "session_id",
            "time_opened",
            "time_last_seen",
            "time_closed",
            "user_id",
            "platform",
        ]