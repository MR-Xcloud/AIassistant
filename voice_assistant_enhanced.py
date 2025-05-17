import os
import time
import azure.cognitiveservices.speech as speechsdk
from chatbot import get_answer, load_data

# Azure Speech Service credentials
AZURE_SPEECH_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
AZURE_REGION = "eastus"

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant"""
        print("🚀 Initializing Voice Assistant...")
        self.speech_config = self._configure_speech_service()
        
        # Pre-load data for faster responses
        print("📚 Loading knowledge base...")
        load_data()
        
        # Configure voice options
        self.voice_options = {
            "default": "en-US-JennyNeural",
            "male": "en-US-GuyNeural",
            "female": "en-US-AriaNeural"
        }
        self.current_voice = self.voice_options["default"]
        
        # Configure speech recognition options
        self.speech_config.speech_recognition_language = "en-US"
        
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
    
    def text_to_speech(self, text):
        """Convert text to speech using Azure Speech Service"""
        print(f"🔊 Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Create a speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
        
        # Synthesize text to speech
        result = speech_synthesizer.speak_text_async(text).get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("✅ Speech synthesis completed")
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"❌ Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return False
    
    def speech_to_text(self):
        """Convert speech to text using Azure Speech Service"""
        print("🎤 Listening... (speak now)")
        
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
    
    def process_command(self, text):
        """Process special commands"""
        if not text:
            return None, False
            
        text_lower = text.lower()
        
        # Check for exit commands
        if any(exit_phrase in text_lower for exit_phrase in ["exit", "quit", "goodbye", "bye"]):
            return "Goodbye! Have a great day!", True
            
        # Check for voice change commands
        if "change voice to male" in text_lower:
            return self.change_voice("male"), False
        elif "change voice to female" in text_lower:
            return self.change_voice("female"), False
        elif "change voice to default" in text_lower:
            return self.change_voice("default"), False
            
        # Check for help command
        if text_lower in ["help", "what can you do", "commands"]:
            help_text = (
                "I can answer questions based on the website data. "
                "You can ask me to change my voice by saying 'change voice to male' or 'change voice to female'. "
                "To exit, say 'goodbye' or 'exit'."
            )
            return help_text, False
            
        # Not a special command, process as a regular query
        return None, False
    
    def run(self):
        """Run the voice assistant in a loop"""
        try:
            # Welcome message
            welcome_message = "Hello! I'm your voice assistant powered by Azure Speech Services. How can I help you today?"
            print(welcome_message)
            self.text_to_speech(welcome_message)
            
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
                print("🧠 Processing your question...")
                response = get_answer(user_input)
                print(f"🤖 Response: {response}")
                
                # Convert response to speech
                self.text_to_speech(response)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure your Azure Speech Service key and region are correct.")
            
            # Try to speak the error if possible
            try:
                self.text_to_speech(f"An error occurred: {str(e)}")
            except:
                pass

def main():
    """Main function to run the voice assistant"""
    print("=" * 50)
    print("🤖 Voice Assistant with Azure Speech Services")
    print("=" * 50)
    
    assistant = VoiceAssistant()
    assistant.run()

if __name__ == "__main__":
    main()