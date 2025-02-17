from rest_framework import serializers
from .models import Transcript


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = ['user', 'message', 'timestamp']
