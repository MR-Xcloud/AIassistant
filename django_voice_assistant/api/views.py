import os
import tempfile
import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import QuerySerializer, TextToSpeechSerializer, SpeechToTextSerializer
from assistant.voice_assistant import get_assistant_response, text_to_speech_file, speech_to_text_file

# Global variable to track sleep mode (in a real app, this would be session-based)
assistant_state = {
    'is_sleeping': False
}

def index(request):
    """Render the main page of the API."""
    return render(request, 'api/index.html')

def index2(request):
    return render(request,'api/index2.html')

class QueryAssistantView(APIView):
    """API view for querying the assistant."""
    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            
            # Check for wait command
            if query.lower().strip() == "wait":
                assistant_state['is_sleeping'] = True
                return Response({'response': "I'm now in sleep mode. Say 'hey assistant' or 'wake up' when you need me."}, status=status.HTTP_200_OK)
            
            # Check if assistant is sleeping
            if assistant_state['is_sleeping']:
                # Check for wake phrases
                if any(wake_phrase in query.lower() for wake_phrase in ["hey assistant", "wake up", "hello assistant"]) or query.lower().strip() in ["hi", "hey", "hello", "hi.", "hey.", "hello."]:
                    assistant_state['is_sleeping'] = False
                    return Response({'response': "I'm awake and ready to help you!"}, status=status.HTTP_200_OK)
                else:
                    # Assistant is sleeping and this is not a wake phrase
                    return Response({'response': "..."}, status=status.HTTP_200_OK)
            
            # Normal query processing
            response = get_assistant_response(query)
            return Response({'response': response}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TextToSpeechView(APIView):
    """API view for text-to-speech conversion."""
    def post(self, request):
        serializer = TextToSpeechSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            audio_file_path = text_to_speech_file(text)
            
            try:
                # Return the audio file
                with open(audio_file_path, 'rb') as audio_file:
                    file_content = audio_file.read()
                
                # Close the file before trying to delete it
                response = Response(file_content, content_type='audio/wav')
                response['Content-Disposition'] = 'attachment; filename="speech.wav"'
                
                # Try to delete the file, but don't fail if we can't
                try:
                    os.unlink(audio_file_path)
                except (PermissionError, OSError):
                    # File might still be in use, we'll let the OS clean it up later
                    pass
                    
                return response
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpeechToTextView(APIView):
    """API view for speech-to-text conversion."""
    def post(self, request):
        serializer = SpeechToTextSerializer(data=request.data)
        if serializer.is_valid():
            audio_file = serializer.validated_data['audio_file']
            
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Convert speech to text
            text = speech_to_text_file(temp_file_path)
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            return Response({'text': text}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def assistant_status(request):
    """Get or update the assistant's status."""
    if request.method == 'POST':
        data = json.loads(request.body)
        if 'is_sleeping' in data:
            assistant_state['is_sleeping'] = data['is_sleeping']
    
    return Response(assistant_state)