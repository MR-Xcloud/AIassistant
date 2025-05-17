"""
Conversation handler for casual chat interactions.
This module provides responses for greetings and casual conversation.
"""

import re
import random

# Dictionary of greeting patterns and responses
GREETINGS = {
    "hello": [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Hello! It's nice to talk with you.",
        "Hi! How may I assist you today?"
    ],
    "hi": [
        "Hi there! How can I help you?",
        "Hello! What can I do for you today?",
        "Hi! How may I assist you?",
        "Hello! What would you like to know?"
    ],
    "hey": [
        "Hey there! How can I help you?",
        "Hi! What can I do for you?",
        "Hey! How may I assist you today?",
        "Hello there! What would you like to know?"
    ],
    "good morning": [
        "Good morning! How can I help you today?",
        "Morning! How may I assist you?",
        "Good morning! What would you like to know?",
        "Morning! What can I do for you today?"
    ],
    "good afternoon": [
        "Good afternoon! How can I help you today?",
        "Afternoon! How may I assist you?",
        "Good afternoon! What would you like to know?",
        "Afternoon! What can I do for you today?"
    ],
    "good evening": [
        "Good evening! How can I help you today?",
        "Evening! How may I assist you?",
        "Good evening! What would you like to know?",
        "Evening! What can I do for you today?"
    ]
}

# Dictionary of how are you patterns and responses
HOW_ARE_YOU = {
    "how are you": [
        "I'm doing well, thank you for asking! How can I help you today?",
        "I'm fine, thanks! What can I do for you?",
        "I'm good! How may I assist you today?",
        "I'm doing great! What would you like to know?"
    ],
    "how's it going": [
        "It's going well! How can I help you today?",
        "Going great! What can I do for you?",
        "Everything's good! How may I assist you?",
        "It's going fine! What would you like to know?"
    ],
    "how do you do": [
        "I'm doing well, thank you! How can I help you today?",
        "I'm fine, thanks for asking! What can I do for you?",
        "I'm good! How may I assist you today?",
        "I'm doing great! What would you like to know?"
    ],
    "what's up": [
        "Not much, just here to help you! What can I do for you?",
        "Just waiting to assist you! What do you need?",
        "All good here! How may I help you today?",
        "Ready to help you! What would you like to know?"
    ]
}

# Dictionary of thank you patterns and responses
THANK_YOU = {
    "thank you": [
        "You're welcome! Is there anything else I can help with?",
        "My pleasure! Anything else you'd like to know?",
        "Happy to help! Do you have any other questions?",
        "You're welcome! Feel free to ask if you need anything else."
    ],
    "thanks": [
        "You're welcome! Anything else I can help with?",
        "No problem! Any other questions?",
        "Happy to help! Need anything else?",
        "You're welcome! Feel free to ask more questions."
    ]
}

# Dictionary of goodbye patterns and responses
GOODBYE = {
    "goodbye": [
        "Goodbye! Have a great day!",
        "Bye! Feel free to ask if you need anything else later.",
        "See you later! Have a wonderful day!",
        "Goodbye! It was nice talking with you."
    ],
    "bye": [
        "Bye! Have a great day!",
        "Goodbye! Feel free to ask if you need anything else later.",
        "See you later! Have a wonderful day!",
        "Bye! It was nice talking with you."
    ],
    "see you": [
        "See you! Have a great day!",
        "Goodbye! Feel free to ask if you need anything else later.",
        "See you later! Have a wonderful day!",
        "Bye! It was nice talking with you."
    ]
}

# Dictionary of other casual conversation patterns and responses
CASUAL = {
    "who are you": [
        "I'm your voice assistant powered by LangChain and Groq. I'm here to help answer your questions about WebMobril.",
        "I'm a voice assistant designed to provide information about WebMobril using LangChain and Groq.",
        "I'm an AI assistant that can answer questions about WebMobril and have conversations with you.",
        "I'm your helpful voice assistant, ready to answer questions about WebMobril and chat with you."
    ],
    "what can you do": [
        "I can answer questions about WebMobril, its products, services, and team. I can also have casual conversations and respond to multiple questions at once.",
        "I'm designed to provide information about WebMobril. I can tell you about their products, services, team members, and more.",
        "I can answer your questions about WebMobril, change my voice, and have conversations with you. Just ask me what you'd like to know!",
        "I can provide information about WebMobril, respond to multiple questions at once, and have casual conversations. How can I help you today?"
    ],
    "tell me about yourself": [
        "I'm your voice assistant powered by LangChain and Groq. I'm designed to answer questions about WebMobril and have conversations with you.",
        "I'm an AI assistant that uses RAG technology to provide accurate information about WebMobril. I can answer questions about their products, services, and team.",
        "I'm a voice assistant created to help you learn about WebMobril. I can answer questions, have conversations, and provide information about the company.",
        "I'm your helpful assistant, built with LangChain and Groq. I'm here to answer your questions about WebMobril and chat with you."
    ]
}

def is_greeting(text):
    """Check if the text is a greeting"""
    text_lower = text.lower().strip()
    
    # Check for exact matches or starts with
    for greeting in GREETINGS:
        if text_lower == greeting or text_lower.startswith(greeting + " "):
            return True
    
    # More precise pattern matching for greetings
    greeting_patterns = [
        r'^hello\b',
        r'^hi\b',
        r'^hey\b',
        r'^good morning\b',
        r'^good afternoon\b',
        r'^good evening\b',
        r'^greetings\b',
        r'^howdy\b'
    ]
    
    for pattern in greeting_patterns:
        if re.match(pattern, text_lower):
            return True
    
    return False

def is_how_are_you(text):
    """Check if the text is asking how the assistant is doing"""
    text_lower = text.lower().strip()
    
    # Check for exact matches or starts with
    for phrase in HOW_ARE_YOU:
        if text_lower == phrase or text_lower.startswith(phrase + " "):
            return True
    
    # More precise pattern matching
    how_are_you_patterns = [
        r'how are you\b',
        r'how\'s it going\b',
        r'how do you do\b',
        r'what\'s up\b',
        r'how have you been\b',
        r'how are things\b'
    ]
    
    for pattern in how_are_you_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def is_thank_you(text):
    """Check if the text is a thank you"""
    text_lower = text.lower().strip()
    
    # Check for exact matches or starts with
    for phrase in THANK_YOU:
        if text_lower == phrase or text_lower.startswith(phrase + " "):
            return True
    
    # More precise pattern matching
    thank_you_patterns = [
        r'thank you\b',
        r'thanks\b',
        r'thank you very much\b',
        r'thanks a lot\b',
        r'appreciate it\b'
    ]
    
    for pattern in thank_you_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def is_goodbye(text):
    """Check if the text is a goodbye"""
    text_lower = text.lower().strip()
    
    # Check for exact matches or starts with
    for phrase in GOODBYE:
        if text_lower == phrase or text_lower.startswith(phrase + " "):
            return True
    
    # More precise pattern matching
    goodbye_patterns = [
        r'goodbye\b',
        r'bye\b',
        r'see you\b',
        r'farewell\b',
        r'so long\b',
        r'take care\b'
    ]
    
    for pattern in goodbye_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def is_casual_question(text):
    """Check if the text is a casual question"""
    text_lower = text.lower().strip()
    
    # Check for exact matches or starts with
    for phrase in CASUAL:
        if text_lower == phrase or text_lower.startswith(phrase + " "):
            return True
    
    # More precise pattern matching
    casual_patterns = [
        r'who are you\b',
        r'what can you do\b',
        r'tell me about yourself\b',
        r'what are you\b',
        r'what is your name\b'
    ]
    
    for pattern in casual_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def get_conversation_response(text):
    """Get a response for conversational text"""
    text_lower = text.lower().strip()
    
    # Check for greetings
    for greeting, responses in GREETINGS.items():
        if text_lower == greeting or text_lower.startswith(greeting + " "):
            return random.choice(responses)
    
    # Check for how are you
    for phrase, responses in HOW_ARE_YOU.items():
        if text_lower == phrase or text_lower.startswith(phrase + " ") or phrase in text_lower:
            return random.choice(responses)
    
    # Check for thank you
    for phrase, responses in THANK_YOU.items():
        if text_lower == phrase or text_lower.startswith(phrase + " ") or phrase in text_lower:
            return random.choice(responses)
    
    # Check for goodbye
    for phrase, responses in GOODBYE.items():
        if text_lower == phrase or text_lower.startswith(phrase + " ") or phrase in text_lower:
            return random.choice(responses)
    
    # Check for casual questions
    for phrase, responses in CASUAL.items():
        if text_lower == phrase or text_lower.startswith(phrase + " ") or phrase in text_lower:
            return random.choice(responses)
    
    # If no match found
    return None