from django.urls import path
from .views import index, QueryAssistantView, TextToSpeechView, SpeechToTextView, assistant_status,index2

urlpatterns = [
    path('', index, name='index'),
    path('index.html',index2,name='index2'),
    path('query/', QueryAssistantView.as_view(), name='query_assistant'),
    path('text-to-speech/', TextToSpeechView.as_view(), name='text_to_speech'),
    path('speech-to-text/', SpeechToTextView.as_view(), name='speech_to_text'),
    path('status/', assistant_status, name='assistant_status'),
]