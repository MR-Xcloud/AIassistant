"""
Complete voice assistant with enhanced RAG, product knowledge, and language awareness.
This version combines all the improvements for a comprehensive voice assistant.
"""

import os
import time
import azure.cognitiveservices.speech as speechsdk
from enhanced_rag import EnhancedRAG, load_enhanced_rag
from language_detector import detect_language, get_hindi_response
import pickle

# Azure Speech Service credentials
AZURE_SPEECH_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
AZURE_REGION = "eastus"

# File to save/load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"

class CompleteVoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant"""
        print("Initializing Complete Voice Assistant...")
        self.speech_config = self._configure_speech_service()
        
        # Load data and initialize RAG
        self.texts = self._load_data()
        self.rag_engine = load_enhanced_rag(self.texts)
        
        # Configure voice options
        self.voice_options = {
            "english_female": "en-US-JennyNeural",
            "english_male": "en-US-GuyNeural",
            "hindi_female": "hi-IN-SwaraNeural",
            "hindi_male": "hi-IN-MadhurNeural"
        }
        
        # Default voices for each language
        self.language_voices = {
            "english": "english_female",
            "hindi": "hindi_female"
        }
        
        # Set default voice
        self.current_voice = self.voice_options[self.language_voices["english"]]
        
        # Configure speech recognition options
        self.speech_config.speech_recognition_language = "en-US"
        
        # Set up speech recognizers for different languages
        self.speech_recognizers = {
            "english": self._create_speech_recognizer("en-US"),
            "hindi": self._create_speech_recognizer("hi-IN")
        }
        
        # Current language
        self.current_language = "english"
    
    def _load_data(self):
        """Load data from cache"""
        if os.path.exists(DATA_CACHE_FILE):
            try:
                print("Loading data from cache...")
                with open(DATA_CACHE_FILE, 'rb') as f:
                    data = pickle.load(f)
                    texts = data['texts']
                print(f"Loaded {len(texts)} text chunks from cache")
                return texts
            except Exception as e:
                print(f"Error loading cache: {e}")
                return []
        else:
            print("No cache file found. Please run update_knowledge_base.py first.")
            return []
    
    def _configure_speech_service(self):
        """Configure the Azure Speech Service"""
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        return speech_config
    
    def _create_speech_recognizer(self, language_code):
        """Create a speech recognizer for a specific language"""
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
        speech_config.speech_recognition_language = language_code
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        return speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    def change_voice(self, voice_type):
        """Change the voice of the assistant"""
        if voice_type in self.voice_options:
            self.current_voice = self.voice_options[voice_type]
            self.speech_config.speech_synthesis_voice_name = self.current_voice
            
            # Update language based on voice
            if "hindi" in voice_type:
                self.current_language = "hindi"
            else:
                self.current_language = "english"
                
            if self.current_language == "hindi":
                return "आवाज़ बदल दी गई है"
            else:
                return f"Voice changed to {voice_type}"
        else:
            return f"Voice type not found. Available options are: {', '.join(self.voice_options.keys())}"
    
    def text_to_speech(self, text, language=None):
        """Convert text to speech using Azure Speech Service"""
        print(f"Speaking: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Determine which voice to use
        if language:
            voice_type = self.language_voices[language]
            voice = self.voice_options[voice_type]
        else:
            voice = self.current_voice
            
        # Set the voice
        self.speech_config.speech_synthesis_voice_name = voice
        
        # Create a speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
        
        # Synthesize text to speech
        result = speech_synthesizer.speak_text_async(text).get()
        
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
        
        # Try to recognize speech in both languages
        results = {}
        
        # First try with the current language
        recognizer = self.speech_recognizers[self.current_language]
        result = recognizer.recognize_once_async().get()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = result.text
            print(f"Recognized ({self.current_language}): {text}")
            
            # Detect language from the recognized text
            detected_language = detect_language(text)
            
            # Update current language if needed
            if detected_language != self.current_language:
                self.current_language = detected_language
                print(f"Language switched to {detected_language}")
                
                # Update voice to match language
                self.change_voice(self.language_voices[detected_language])
            
            return text
        else:
            print(f"No speech recognized in {self.current_language}")
            
            # Try the other language
            other_language = "hindi" if self.current_language == "english" else "english"
            recognizer = self.speech_recognizers[other_language]
            result = recognizer.recognize_once_async().get()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text
                print(f"Recognized ({other_language}): {text}")
                
                # Update current language
                self.current_language = other_language
                print(f"Language switched to {other_language}")
                
                # Update voice to match language
                self.change_voice(self.language_voices[other_language])
                
                return text
        
        print("No speech could be recognized in any language")
        return None
    
    def process_command(self, text):
        """Process special commands"""
        if not text:
            return None, False
            
        text_lower = text.lower()
        
        # Check for exit commands in both languages
        if any(exit_phrase in text_lower for exit_phrase in ["exit", "quit", "goodbye", "bye", "अलविदा", "बाय"]):
            if self.current_language == "hindi":
                return "अलविदा! आपका दिन शुभ हो!", True
            else:
                return "Goodbye! Have a great day!", True
            
        # Check for voice change commands
        if "change voice to english female" in text_lower or "अंग्रेजी महिला आवाज़" in text_lower:
            return self.change_voice("english_female"), False
        elif "change voice to english male" in text_lower or "अंग्रेजी पुरुष आवाज़" in text_lower:
            return self.change_voice("english_male"), False
        elif "change voice to hindi female" in text_lower or "हिंदी महिला आवाज़" in text_lower:
            return self.change_voice("hindi_female"), False
        elif "change voice to hindi male" in text_lower or "हिंदी पुरुष आवाज़" in text_lower:
            return self.change_voice("hindi_male"), False
            
        # Check for help command
        if any(help_phrase in text_lower for help_phrase in ["help", "what can you do", "commands", "मदद", "आप क्या कर सकते हैं"]):
            if self.current_language == "hindi":
                help_text = (
                    "मैं आपके सवालों का जवाब उसी भाषा में दे सकता हूँ जिसमें आप पूछते हैं। "
                    "आप मेरी आवाज़ बदल सकते हैं 'हिंदी महिला आवाज़' या 'अंग्रेजी पुरुष आवाज़' कहकर। "
                    "बाहर निकलने के लिए, 'अलविदा' या 'बाय' कहें।"
                )
            else:
                help_text = (
                    "I can answer questions in the same language you ask. "
                    "You can change my voice by saying 'change voice to hindi female' or 'english male'. "
                    "To exit, say 'goodbye' or 'exit'."
                )
            return help_text, False
            
        # Not a special command, process as a regular query
        return None, False
    
    def run(self):
        """Run the voice assistant in a loop"""
        try:
            # Welcome message in both languages
            english_welcome = "Hello! I'm your complete voice assistant with enhanced knowledge. I'll respond in the same language you use to ask questions."
            hindi_welcome = "नमस्ते! मैं बेहतर ज्ञान के साथ आपका पूर्ण वॉइस असिस्टेंट हूँ। मैं आपके सवालों का जवाब उसी भाषा में दूंगा जिसमें आप पूछेंगे।"
            
            print(english_welcome)
            self.text_to_speech(english_welcome, "english")
            self.text_to_speech(hindi_welcome, "hindi")
            
            # Main loop
            while True:
                # Get speech input
                user_input = self.speech_to_text()
                
                # Check if we got valid input
                if not user_input:
                    if self.current_language == "hindi":
                        error_message = "मैं समझ नहीं पाया। क्या आप फिर से कह सकते हैं?"
                    else:
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
                english_response = self.rag_engine.retrieve(user_input)
                print(f"English Response: {english_response}")
                
                # Convert to Hindi if needed
                if self.current_language == "hindi":
                    hindi_response = get_hindi_response(english_response)
                    print(f"Hindi Response: {hindi_response}")
                    self.text_to_speech(hindi_response)
                else:
                    self.text_to_speech(english_response)
        
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure your Azure Speech Service key and region are correct.")
            
            # Try to speak the error if possible
            try:
                error_message = f"An error occurred: {str(e)}"
                if self.current_language == "hindi":
                    error_message = f"एक त्रुटि हुई: {str(e)}"
                self.text_to_speech(error_message)
            except:
                pass

def main():
    """Main function to run the complete voice assistant"""
    print("=" * 50)
    print("Complete Voice Assistant")
    print("=" * 50)
    
    assistant = CompleteVoiceAssistant()
    assistant.run()

if __name__ == "__main__":
    main()