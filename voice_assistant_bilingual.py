"""
Bilingual voice assistant that answers in both English and Hindi.
This version combines the enhanced voice assistant features with bilingual capabilities.
"""

import os
import time
import azure.cognitiveservices.speech as speechsdk
from improved_chatbot import get_answer, load_data
from translator import translate_text

# Azure Speech Service credentials
AZURE_SPEECH_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
AZURE_REGION = "eastus"

class BilingualVoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant"""
        print("Initializing Bilingual Voice Assistant...")
        self.speech_config = self._configure_speech_service()
        
        # Pre-load data for faster responses
        print("Loading knowledge base...")
        load_data()
        
        # Configure voice options
        self.voice_options = {
            "english_female": "en-US-JennyNeural",
            "english_male": "en-US-GuyNeural",
            "hindi_female": "hi-IN-SwaraNeural",
            "hindi_male": "hi-IN-MadhurNeural"
        }
        self.current_voice = self.voice_options["english_female"]
        
        # Configure speech recognition options
        self.speech_config.speech_recognition_language = "en-US"
        
        # Language settings
        self.current_language = "english"  # Can be "english" or "hindi"
        self.bilingual_mode = True  # Whether to respond in both languages
        
    def _configure_speech_service(self):
        """Configure the Azure Speech Service"""
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        return speech_config
    
    def change_voice(self, voice_type):
        """Change the voice of the assistant"""
        if voice_type in self.voice_options:
            self.current_voice = self.voice_options[voice_type]
            self.speech_config.speech_synthesis_voice_name = self.current_voice
            return f"Voice changed to {voice_type}"
        else:
            return f"Voice type not found. Available options are: {', '.join(self.voice_options.keys())}"
    
    def change_language(self, language):
        """Change the primary language of the assistant"""
        if language.lower() == "english":
            self.current_language = "english"
            self.change_voice("english_female")
            return "Language changed to English"
        elif language.lower() == "hindi":
            self.current_language = "hindi"
            self.change_voice("hindi_female")
            return "Language changed to Hindi"
        else:
            return "Unsupported language. Available options are: English, Hindi"
    
    def toggle_bilingual_mode(self):
        """Toggle bilingual mode on/off"""
        self.bilingual_mode = not self.bilingual_mode
        if self.bilingual_mode:
            return "Bilingual mode enabled. I will respond in both English and Hindi."
        else:
            return f"Bilingual mode disabled. I will respond in {self.current_language} only."
    
    def text_to_speech(self, text, language=None):
        """Convert text to speech using Azure Speech Service"""
        print(f"Speaking: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Set the voice based on language if specified
        original_voice = self.speech_config.speech_synthesis_voice_name
        if language:
            if language.lower() == "hindi":
                self.speech_config.speech_synthesis_voice_name = self.voice_options["hindi_female"]
            elif language.lower() == "english":
                self.speech_config.speech_synthesis_voice_name = self.voice_options["english_female"]
        
        # Create a speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
        
        # Synthesize text to speech
        result = speech_synthesizer.speak_text_async(text).get()
        
        # Restore original voice
        if language:
            self.speech_config.speech_synthesis_voice_name = original_voice
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesis completed")
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return False
    
    def speech_to_text(self):
        """Convert speech to text using Azure Speech Service"""
        print("Listening... (speak now)")
        
        # Create a speech recognizer
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, 
            audio_config=audio_config
        )
        
        # Start speech recognition
        result = speech_recognizer.recognize_once_async().get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognized: {result.text}")
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized")
            return None
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return None
    
    def process_command(self, text):
        """Process special commands"""
        if not text:
            return None, False
            
        text_lower = text.lower()
        
        # Check for exit commands
        if any(exit_phrase in text_lower for exit_phrase in ["exit", "quit", "goodbye", "bye"]):
            return "Goodbye! Have a great day!", True
            
        # Check for voice change commands
        if "change voice to english female" in text_lower:
            return self.change_voice("english_female"), False
        elif "change voice to english male" in text_lower:
            return self.change_voice("english_male"), False
        elif "change voice to hindi female" in text_lower:
            return self.change_voice("hindi_female"), False
        elif "change voice to hindi male" in text_lower:
            return self.change_voice("hindi_male"), False
            
        # Check for language change commands
        if "change language to english" in text_lower:
            return self.change_language("english"), False
        elif "change language to hindi" in text_lower:
            return self.change_language("hindi"), False
            
        # Check for bilingual mode commands
        if "enable bilingual mode" in text_lower or "turn on bilingual mode" in text_lower:
            self.bilingual_mode = True
            return "Bilingual mode enabled. I will respond in both English and Hindi.", False
        elif "disable bilingual mode" in text_lower or "turn off bilingual mode" in text_lower:
            self.bilingual_mode = False
            return f"Bilingual mode disabled. I will respond in {self.current_language} only.", False
            
        # Check for help command
        if text_lower in ["help", "what can you do", "commands"]:
            help_text = (
                "I can answer questions in both English and Hindi. "
                "You can change my voice by saying 'change voice to english female/male' or 'hindi female/male'. "
                "You can change my language by saying 'change language to english/hindi'. "
                "You can enable or disable bilingual mode by saying 'enable/disable bilingual mode'. "
                "To exit, say 'goodbye' or 'exit'."
            )
            return help_text, False
            
        # Not a special command, process as a regular query
        return None, False
    
    def run(self):
        """Run the voice assistant in a loop"""
        try:
            # Welcome message
            welcome_message = "Hello! I'm your bilingual voice assistant. I can answer in both English and Hindi. How can I help you today?"
            hindi_welcome = "नमस्ते! मैं आपका द्विभाषी वॉइस असिस्टेंट हूँ। मैं अंग्रेजी और हिंदी दोनों में जवाब दे सकता हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?"
            
            print(welcome_message)
            self.text_to_speech(welcome_message, "english")
            self.text_to_speech(hindi_welcome, "hindi")
            
            # Main loop
            while True:
                # Get speech input
                user_input = self.speech_to_text()
                
                # Check if we got valid input
                if not user_input:
                    error_message = "I didn't catch that. Could you please try again?"
                    print(error_message)
                    self.text_to_speech(error_message)
                    continue
                
                # Process commands
                command_response, should_exit = self.process_command(user_input)
                if command_response:
                    print(command_response)
                    self.text_to_speech(command_response)
                    if should_exit:
                        break
                    continue
                
                # Process the query and get response
                print("Processing your question...")
                english_response = get_answer(user_input)
                print(f"English Response: {english_response}")
                
                # If bilingual mode is enabled, translate to Hindi
                if self.bilingual_mode:
                    print("Translating to Hindi...")
                    hindi_response = translate_text(english_response, "hi", "en")
                    print(f"Hindi Response: {hindi_response}")
                    
                    # Speak responses in both languages
                    self.text_to_speech(english_response, "english")
                    self.text_to_speech(hindi_response, "hindi")
                else:
                    # Speak in the current language only
                    if self.current_language == "hindi":
                        hindi_response = translate_text(english_response, "hi", "en")
                        self.text_to_speech(hindi_response)
                    else:
                        self.text_to_speech(english_response)
        
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure your Azure Speech Service key and region are correct.")
            
            # Try to speak the error if possible
            try:
                self.text_to_speech(f"An error occurred: {str(e)}")
            except:
                pass

def main():
    """Main function to run the bilingual voice assistant"""
    print("=" * 50)
    print("Bilingual Voice Assistant (English & Hindi)")
    print("=" * 50)
    
    assistant = BilingualVoiceAssistant()
    assistant.run()

if __name__ == "__main__":
    main()