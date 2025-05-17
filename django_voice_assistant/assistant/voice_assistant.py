"""
Voice assistant API module for Django.
This module provides functions for the voice assistant API.
"""

import os
import tempfile
import azure.cognitiveservices.speech as speechsdk
from .rag_langchain import initialize_rag, get_rag_answer
from .conversation_handler import is_greeting, is_how_are_you, is_thank_you, is_goodbye, is_casual_question, get_conversation_response

# Azure Speech Service credentials
AZURE_SPEECH_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
AZURE_REGION = "eastus"

# Initialize RAG system
rag_data = None

def initialize():
    """Initialize the RAG system if not already initialized"""
    global rag_data
    if rag_data is None:
        rag_data = initialize_rag()
    return rag_data

def get_assistant_response(query):
    """Get a response from the assistant for a text query"""
    # Initialize RAG system if needed
    initialize()
    
    # Direct check for simple greetings
    if query.lower().strip() in ["hi", "hey", "hello", "hi.", "hey.", "hello."]:
        return "Hello! How can I help you today?"
    
    # Hardcoded corrections for specific queries
    query_lower = query.lower().strip()
    
    # Executive information corrections
    if "president" in query_lower or "rajeev saxena" in query_lower:
        return "Rajeev Saxena is the President of WebMobril."
    
    if "poonam yadav" in query_lower or ("poonam" in query_lower and "hr" in query_lower):
        return "Poonam Yadav is the Associate Vice President - Human Resource at WebMobril."
    
    if "vivek" in query_lower and ("upadhyay" in query_lower or "nand" in query_lower):
        return "Viveka Nand Upadhyay is the Associate Vice President - Delivery at WebMobril."
    
    if "swaraj gupta" in query_lower:
        return "Swaraj Gupta is the Associate Director - Technology at WebMobril."
    
    if "bed prakash" in query_lower or "general manager" in query_lower:
        return "Bed Prakash is the General Manager - Admin & Accounts at WebMobril."
    
    # Check if the query is a conversational input
    if is_greeting(query) or is_how_are_you(query) or is_thank_you(query) or is_goodbye(query) or is_casual_question(query):
        response = get_conversation_response(query)
        if response:
            return response
    
    # Process the query and get response
    response = get_rag_answer(query, rag_data)
    return response

def text_to_speech_file(text):
    """Convert text to speech and save to a file"""
    # Configure speech service
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_file_path = temp_file.name
    temp_file.close()
    
    # Configure audio output
    audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file_path)
    
    # Create a speech synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    # Synthesize text to speech
    result = speech_synthesizer.speak_text_async(text).get()
    
    # Check result
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise Exception("Speech synthesis failed")
    
    return temp_file_path

def speech_to_text_file(audio_file_path):
    """Convert speech from a file to text"""
    # Configure speech service
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
    
    # Configure audio input
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    
    # Create a speech recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Start speech recognition
    result = speech_recognizer.recognize_once_async().get()
    
    # Check result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized"
    elif result.reason == speechsdk.ResultReason.Canceled:
        return "Speech recognition canceled"
    
    return "Unknown error"