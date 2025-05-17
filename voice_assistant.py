import os
import azure.cognitiveservices.speech as speechsdk
from chatbot import get_answer

# Azure Speech Service credentials
AZURE_SPEECH_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
AZURE_REGION = "eastus"

def configure_speech_service():
    """Configure the Azure Speech Service"""
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
    
    # Set speech synthesis voice (optional)
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
    
    return speech_config

def text_to_speech(text, speech_config):
    """Convert text to speech using Azure Speech Service"""
    print(f"🔊 Speaking: {text[:50]}...")
    
    # Create a speech synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    # Synthesize text to speech
    result = speech_synthesizer.speak_text_async(text).get()
    
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("✅ Speech synthesis completed")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"❌ Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

def speech_to_text(speech_config):
    """Convert speech to text using Azure Speech Service"""
    print("🎤 Listening... (speak now)")
    
    # Create a speech recognizer
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Start speech recognition
    print("Say something...")
    result = speech_recognizer.recognize_once_async().get()
    
    # Check result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"🔍 Recognized: {result.text}")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("❌ No speech could be recognized")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"❌ Speech recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
        return None

def run_voice_assistant():
    """Run the voice assistant in a loop"""
    print("🤖 Voice Assistant is starting...")
    print("🔧 Configuring Azure Speech Service...")
    
    try:
        # Configure speech service
        speech_config = configure_speech_service()
        
        # Welcome message
        welcome_message = "Hello! I'm your voice assistant. How can I help you today?"
        print(welcome_message)
        text_to_speech(welcome_message, speech_config)
        
        # Main loop
        while True:
            # Get speech input
            user_input = speech_to_text(speech_config)
            
            # Check if we got valid input
            if not user_input:
                error_message = "I didn't catch that. Could you please try again?"
                print(error_message)
                text_to_speech(error_message, speech_config)
                continue
            
            # Check for exit command
            if any(exit_phrase in user_input.lower() for exit_phrase in ["exit", "quit", "goodbye", "bye"]):
                farewell = "Goodbye! Have a great day!"
                print(farewell)
                text_to_speech(farewell, speech_config)
                break
            
            # Process the query and get response
            response = get_answer(user_input)
            print(f"🤖 Response: {response}")
            
            # Convert response to speech
            text_to_speech(response, speech_config)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your Azure Speech Service key and region are correct.")

if __name__ == "__main__":
    run_voice_assistant()