"""
Language detector module to identify the language of input text.
Uses simple pattern matching for basic language detection.
"""

def detect_language(text):
    """
    Detect if text is in Hindi or English.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: 'hindi' if Hindi is detected, 'english' otherwise
    """
    # Common Hindi words and patterns
    hindi_words = [
        'है', 'हैं', 'का', 'की', 'के', 'में', 'से', 'को', 'पर', 'कौन', 'क्या', 'कब', 
        'कहां', 'क्यों', 'कैसे', 'नमस्ते', 'धन्यवाद', 'शुभ', 'अच्छा', 'बुरा', 'कंपनी',
        'कंपनी', 'सीईओ', 'संस्थापक', 'कहाँ', 'स्थित', 'मुख्यालय', 'कार्यालय'
    ]
    
    # Hindi question patterns
    hindi_patterns = [
        'कौन है', 'क्या है', 'कहां है', 'कब', 'कैसे', 'क्यों', 'बताओ', 'बताइए'
    ]
    
    # Convert text to lowercase for easier matching
    text_lower = text.lower()
    
    # Check for Hindi words and patterns
    for word in hindi_words:
        if word in text_lower:
            return 'hindi'
            
    for pattern in hindi_patterns:
        if pattern in text_lower:
            return 'hindi'
    
    # Default to English if no Hindi patterns detected
    return 'english'

# Hindi translations for common responses
HINDI_RESPONSES = {
    "Ajay Saraswat is the CEO and Founder of WebMobril.": 
        "अजय सारस्वत WebMobril के CEO और संस्थापक हैं।",
    
    "The CEO of WebMobril is Ajay Saraswat.": 
        "WebMobril के CEO अजय सारस्वत हैं।",
    
    "The founder of WebMobril is Ajay Saraswat.": 
        "WebMobril के संस्थापक अजय सारस्वत हैं।",
    
    "WebMobril was founded by Ajay Saraswat.": 
        "WebMobril की स्थापना अजय सारस्वत ने की थी।",
    
    "WebMobril was founded in 2014.": 
        "WebMobril की स्थापना 2014 में हुई थी।",
    
    "WebMobril has been in business since 2014.": 
        "WebMobril 2014 से व्यापार में है।",
    
    "WebMobril is headquartered in Noida, India with offices in India, USA, UK.": 
        "WebMobril का मुख्यालय नोएडा, भारत में है और भारत, अमेरिका, यूके में कार्यालय हैं।",
    
    "WebMobril offers Web Development, Mobile App Development, UI/UX Design, Digital Marketing, Enterprise Solutions.": 
        "WebMobril वेब डेवलपमेंट, मोबाइल ऐप डेवलपमेंट, UI/UX डिज़ाइन, डिजिटल मार्केटिंग, एंटरप्राइज़ सॉल्यूशंस प्रदान करता है।",
    
    "I don't have information on that topic.": 
        "मेरे पास इस विषय पर जानकारी नहीं है।",
    
    "I didn't catch that. Could you please try again?": 
        "मैं समझ नहीं पाया। क्या आप फिर से कह सकते हैं?",
    
    "Goodbye! Have a great day!": 
        "अलविदा! आपका दिन शुभ हो!",
    
    "Hello! I'm your voice assistant. How can I help you today?": 
        "नमस्ते! मैं आपका वॉइस असिस्टेंट हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?"
}

def get_hindi_response(english_text):
    """
    Get Hindi translation for common English responses.
    
    Args:
        english_text (str): The English text to translate
        
    Returns:
        str: Hindi translation if available, otherwise the original English text
    """
    return HINDI_RESPONSES.get(english_text, english_text)