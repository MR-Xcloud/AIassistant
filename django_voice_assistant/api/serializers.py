"""
Serializers for the API app.
"""

from rest_framework import serializers

class QuerySerializer(serializers.Serializer):
    """Serializer for query requests."""
    query = serializers.CharField(required=True)

class TextToSpeechSerializer(serializers.Serializer):
    """Serializer for text-to-speech requests."""
    text = serializers.CharField(required=True)

class SpeechToTextSerializer(serializers.Serializer):
    """Serializer for speech-to-text requests."""
    audio_file = serializers.FileField(required=True)