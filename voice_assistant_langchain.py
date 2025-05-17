"""
Voice assistant using LangChain, FAISS, and Groq.
This module provides a voice interface for the RAG system.
"""

import os
import time
import threading
import queue
import re
import azure.cognitiveservices.speech as speechsdk
from rag_langchain import initialize_rag, get_rag_answer
from conversation_handler import is_greeting, is_how_are_you, is_thank_you, is_goodbye, is_casual_question, get_conversation_response

# Azure Speech Service credentials
# AZURE_SPEECH_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
# AZURE_REGION = "eastus"
AZURE_SPEECH_KEY = "B0Vs64elOFZVD2n3dhkPW5vC6jgZfkQj4CWAnkV0LqAJebumiLndJQQJ99BEACYeBjFXJ3w3AAAYACOGZAG0"
AZURE_REGION = "eastus"
# AZURE_SPEECH_KEY = "FZubcHJqy5M6RYTJ873RmsX0xDu27lR7UzTBdHuP82G4TQNexmTnJQQJ99BCAC3pKaRXJ3w3AAAYACOGKYv5"
# AZURE_REGION = "eastasia"
class LangChainVoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant"""
        print("Initializing LangChain Voice Assistant...")
        self.speech_config = self._configure_speech_service()
        
        # Initialize RAG system
        print("Initializing RAG system with LangChain...")
        self.rag_data = initialize_rag()
        
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
        
        # Flag to control speech output
        self.stop_speaking = False
        self.is_speaking = False
        self.speech_synthesizer = None
        self.just_stopped = False
        
        # Sleep mode flags
        self.is_sleeping = False
        self.wake_phrases = ["hey assistant", "wake up", "hello assistant", "hey there"]
        
        # Create a queue for stop commands
        self.command_queue = queue.Queue()
        
        # Start the command listener thread
        self.command_listener_active = True
        self.command_listener_thread = threading.Thread(target=self._continuous_command_listener)
        self.command_listener_thread.daemon = True
        self.command_listener_thread.start()
        
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
    
    def _continuous_command_listener(self):
        """Continuously listen for commands in the background"""
        while self.command_listener_active:
            if self.is_speaking:
                # Create a speech recognizer for commands
                command_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
                command_config.speech_recognition_language = "en-US"
                audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
                
                # Use keyword recognition to detect "stop"
                command_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=command_config,
                    audio_config=audio_config
                )
                
                # Start listening for a short duration
                try:
                    result = command_recognizer.recognize_once_async().get()
                    
                    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                        text = result.text.lower()
                        if any(stop_word in text for stop_word in ["stop", "quiet", "silence", "enough", "shut", "pause"]):
                            print("Stop command detected!")
                            self.command_queue.put("stop")
                            
                            # Immediately stop speaking
                            if self.speech_synthesizer:
                                self.speech_synthesizer.stop_speaking_async()
                                self.stop_speaking = True
                                self.just_stopped = True
                except Exception as e:
                    print(f"Command listener error: {e}")
            
            # Sleep briefly to avoid consuming too many resources
            time.sleep(0.1)
    
    def _split_into_chunks(self, text, max_length=500):
        """Split text into manageable chunks for speech synthesis"""
        # First try to split by paragraphs
        paragraphs = text.split('\n')
        chunks = []
        
        for paragraph in paragraphs:
            # If paragraph is short enough, add it as is
            if len(paragraph.strip()) == 0:
                continue
                
            if len(paragraph) <= max_length:
                chunks.append(paragraph)
            else:
                # Split long paragraphs into sentences
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                current_chunk = ""
                
                for sentence in sentences:
                    if len(sentence.strip()) == 0:
                        continue
                        
                    # If adding this sentence would make the chunk too long, start a new chunk
                    if len(current_chunk) + len(sentence) > max_length:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sentence
                    else:
                        if current_chunk:
                            current_chunk += " " + sentence
                        else:
                            current_chunk = sentence
                
                # Add the last chunk if it's not empty
                if current_chunk:
                    chunks.append(current_chunk)
        
        return chunks
    
    def text_to_speech(self, text):
        """Convert text to speech using Azure Speech Service"""
        print(f"Speaking: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Reset stop flag
        self.stop_speaking = False
        self.is_speaking = True
        
        try:
            # Create a speech synthesizer
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)
            
            # Split text into manageable chunks
            chunks = self._split_into_chunks(text)
            
            # Speak each chunk, checking for stop command between chunks
            for chunk in chunks:
                if self.stop_speaking:
                    print("Speech stopped by command")
                    break
                    
                # Check if there's a stop command in the queue
                try:
                    if not self.command_queue.empty():
                        command = self.command_queue.get_nowait()
                        if command == "stop":
                            print("Stop command processed")
                            self.stop_speaking = True
                            self.just_stopped = True
                            break
                except queue.Empty:
                    pass
                    
                # Speak the chunk
                try:
                    result = self.speech_synthesizer.speak_text_async(chunk).get()
                    
                    # Check result
                    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
                        print(f"Speech synthesis issue: {result.reason}")
                        if result.reason == speechsdk.ResultReason.Canceled:
                            cancellation = result.cancellation_details
                            print(f"Cancellation reason: {cancellation.reason}")
                            if cancellation.reason == speechsdk.CancellationReason.Error:
                                print(f"Error details: {cancellation.error_details}")
                        break
                except Exception as e:
                    print(f"Error in speech synthesis: {e}")
                    break
                    
                # Small pause between chunks
                time.sleep(0.1)
            
        except Exception as e:
            print(f"Error in text_to_speech: {e}")
        
        finally:
            # Set speaking flag to False
            self.is_speaking = False
            self.speech_synthesizer = None
        
        return not self.stop_speaking
    
    def speech_to_text(self):
        """Convert speech to text using Azure Speech Service"""
        # If we just stopped speaking, wait a moment before listening again
        if self.just_stopped:
            print("Pausing briefly after stop command...")
            time.sleep(1)  # Wait a second
            self.just_stopped = False
            
            # Clear any pending commands
            while not self.command_queue.empty():
                try:
                    self.command_queue.get_nowait()
                except queue.Empty:
                    break
        
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
        
        # Check for wake command if in sleep mode
        if self.is_sleeping and any(wake_phrase in text_lower for wake_phrase in self.wake_phrases):
            self.is_sleeping = False
            return "I'm awake and ready to help you!", False
        
        # Check for exit commands
        if any(exit_phrase in text_lower for exit_phrase in ["exit", "quit", "goodbye", "bye"]):
            return "Goodbye! Have a great day!", True
            
        # Check for stop command
        if any(stop_phrase in text_lower for stop_phrase in ["stop", "quiet", "silence", "enough"]) and self.is_speaking:
            self.stop_speaking = True
            self.just_stopped = True
            if self.speech_synthesizer:
                self.speech_synthesizer.stop_speaking_async()
            return "I'll stop speaking now.", False
        
        # Check for wait command - go to sleep immediately
        if "wait" in text_lower:
            # Enter sleep mode immediately
            self.is_sleeping = True
            return "I'm now in sleep mode.", False
  
        # Check for voice change commands
        if "change voice to english female" in text_lower:
            return self.change_voice("english_female"), False
        elif "change voice to english male" in text_lower:
            return self.change_voice("english_male"), False
        elif "change voice to hindi female" in text_lower:
            return self.change_voice("hindi_female"), False
        elif "change voice to hindi male" in text_lower:
            return self.change_voice("hindi_male"), False
            
        # Check for help command
        if text_lower in ["help", "what can you do", "commands"]:
            help_text = (
                "I am here to solve your queries. Please let me know "
                "You can change my voice by saying 'change voice to english female/male' or 'hindi female/male'. "
                "Say 'stop' to interrupt me when I'm speaking. "
                "Say 'wait' to enter sleep mode. "
                "Say 'hey assistant' or 'wake up' to wake me from sleep mode. "
                "To exit, say 'goodbye' or 'exit'."
            )
            return help_text, False
            
        # Not a special command, process as a regular query
        return None, False
    
    def handle_conversation(self, text):
        """Handle conversational inputs like greetings"""
        # Direct check for simple greetings
        if text.lower().strip() in ["hi", "hey", "hello", "hi.", "hey.", "hello."]:
            return "Hello! How can I help you today?"
            
        # Check if the input is conversational
        if is_greeting(text) or is_how_are_you(text) or is_thank_you(text) or is_goodbye(text) or is_casual_question(text):
            response = get_conversation_response(text)
            if response:
                return response
        
        # Not a conversational input
        return None
    
    def run(self):
        """Run the voice assistant in a loop"""
        try:
            # Welcome message
            welcome_message = "Hello! I am WebMobril's voice assistant. How can I help you today?"
            print(welcome_message)
            self.text_to_speech(welcome_message)
            
            # Main loop
            while True:
                # If in sleep mode, use a different message and only listen for wake commands
                if self.is_sleeping:
                    print("In sleep mode.")
                    user_input = self.speech_to_text()
                    
                    if user_input:
                        user_input_lower = user_input.lower().strip()
                        # Check for wake phrases or simple greetings
                        if (any(wake_phrase in user_input_lower for wake_phrase in self.wake_phrases) or 
                            user_input_lower in ["hi", "hey", "hello", "hi.", "hey.", "hello."]):
                            self.is_sleeping = False
                            wake_response = "Yes please!"
                            print(wake_response)
                            self.text_to_speech(wake_response)
                    continue
                
                # Normal operation mode
                # Get speech input
                user_input = self.speech_to_text()
                
                # Check if we got valid input
                if not user_input:
                    error_message = "Pardon, repeat?"
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
                
                # Check for conversational inputs
                conversation_response = self.handle_conversation(user_input)
                if conversation_response:
                    print(f"Conversation response: {conversation_response}")
                    self.text_to_speech(conversation_response)
                    continue
                
                # Process the query and get response
                print("Processing your question with LangChain and Groq...")
                response = get_rag_answer(user_input, self.rag_data)
                print(f"Response: {response}")
                
                # Convert response to speech
                self.text_to_speech(response)
        
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure your Azure Speech Service key and region are correct.")
            
            # Try to speak the error if possible
            try:
                self.text_to_speech(f"An error occurred: {str(e)}")
            except:
                pass
        
        finally:
            # Clean up resources
            self.command_listener_active = False
            if self.speech_synthesizer:
                self.speech_synthesizer.stop_speaking_async()

def main():
    """Main function to run the LangChain voice assistant"""
    print("=" * 50)
    print("Voice Assistant")
    print("=" * 50)
    
    assistant = LangChainVoiceAssistant()
    assistant.run()

if __name__ == "__main__":
    main()