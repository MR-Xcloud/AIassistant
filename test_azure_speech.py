"""
Test script for Azure Speech Services.
This script tests both speech-to-text and text-to-speech functionality
to verify that your Azure Speech Service credentials are working correctly.
"""

import os
import time
import azure.cognitiveservices.speech as speechsdk

# Azure Speech Service credentials
AZURE_SPEECH_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
AZURE_REGION = "eastus"

def test_text_to_speech():
    """Test text-to-speech functionality"""
    print("\n🔊 Testing Text-to-Speech...")
    
    try:
        # Configure speech service
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        
        # Create a speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # Test message
        test_message = "This is a test of the Azure Speech Service text-to-speech functionality."
        print(f"Speaking: \"{test_message}\"")
        
        # Synthesize text to speech
        result = speech_synthesizer.speak_text_async(test_message).get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("✅ Text-to-Speech test successful!")
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"❌ Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return False
    
    except Exception as e:
        print(f"❌ Error in Text-to-Speech test: {e}")
        return False

def test_speech_to_text():
    """Test speech-to-text functionality"""
    print("\n🎤 Testing Speech-to-Text...")
    print("Please speak a simple phrase when prompted.")
    
    try:
        # Configure speech service
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
        
        # Create a speech recognizer
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # Prompt user
        print("\nPlease speak now...")
        
        # Start speech recognition
        result = speech_recognizer.recognize_once_async().get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"✅ Speech-to-Text test successful!")
            print(f"Recognized text: \"{result.text}\"")
            return True
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("❌ No speech could be recognized")
            return False
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"❌ Speech recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return False
    
    except Exception as e:
        print(f"❌ Error in Speech-to-Text test: {e}")
        return False

def test_azure_speech():
    """Run tests for Azure Speech Services"""
    print("=" * 60)
    print("🧪 AZURE SPEECH SERVICES TEST")
    print("=" * 60)
    
    print("\nThis test will verify that your Azure Speech Service credentials are working correctly.")
    print(f"Using Speech Key: {AZURE_SPEECH_KEY[:5]}...{AZURE_SPEECH_KEY[-5:]}")
    print(f"Using Region: {AZURE_REGION}")
    
    # Test text-to-speech
    tts_success = test_text_to_speech()
    
    # Small delay between tests
    time.sleep(1)
    
    # Test speech-to-text
    stt_success = test_speech_to_text()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Text-to-Speech: {'✅ PASSED' if tts_success else '❌ FAILED'}")
    print(f"Speech-to-Text: {'✅ PASSED' if stt_success else '❌ FAILED'}")
    
    if tts_success and stt_success:
        print("\n✅ All tests passed! Your Azure Speech Service is configured correctly.")
    else:
        print("\n❌ Some tests failed. Please check your Azure Speech Service credentials.")
    
    print("\nPress Enter to continue...")
    input()

if __name__ == "__main__":
    test_azure_speech()