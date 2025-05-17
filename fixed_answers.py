"""
Fixed answers module for specific questions.
This provides hardcoded answers for common questions about the company.
"""

# Dictionary of fixed answers for specific questions
FIXED_ANSWERS = {
    # CEO and leadership
    "ajay saraswat": "Ajay Saraswat is the CEO and Founder of WebMobril.",
    "who is ajay saraswat": "Ajay Saraswat is the CEO and Founder of WebMobril.",
    "who is the ceo": "Ajay Saraswat is the CEO of WebMobril.",
    "who is the founder": "Ajay Saraswat is the Founder of WebMobril.",
    "who founded the company": "WebMobril was founded by Ajay Saraswat.",
    "who started the company": "WebMobril was started by Ajay Saraswat.",
    "ceo name": "The CEO of WebMobril is Ajay Saraswat.",
    "founder name": "The founder of WebMobril is Ajay Saraswat.",
    
    # Company information
    "when was the company founded": "WebMobril was founded in 2014.",
    "company founding date": "WebMobril was established in 2014.",
    "when did webmobril start": "WebMobril started operations in 2014.",
    "how old is the company": "WebMobril has been in business since 2014.",
    
    # Location
    "where is the company located": "WebMobril is headquartered in Noida, India with offices in the USA and UK.",
    "company location": "WebMobril's headquarters are in Noida, India.",
    "where is webmobril": "WebMobril is based in Noida, India with international offices.",
    "office locations": "WebMobril has offices in India, the USA, and the UK.",
    
    # Services
    "what services": "WebMobril offers web development, mobile app development, UI/UX design, digital marketing, and enterprise solutions.",
    "what does webmobril do": "WebMobril specializes in web and mobile app development, UI/UX design, and digital marketing services.",
    "services offered": "WebMobril provides web and mobile app development, UI/UX design, digital marketing, and enterprise solutions.",
    "main services": "WebMobril's main services include web development, mobile app development, UI/UX design, and digital marketing.",
}

def get_fixed_answer(query):
    """
    Check if there's a fixed answer for the query.
    
    Args:
        query (str): The user's question
        
    Returns:
        str or None: The fixed answer if available, None otherwise
    """
    if not query:
        return None
        
    # Clean and normalize the query
    clean_query = query.lower().strip()
    if clean_query.endswith('?'):
        clean_query = clean_query[:-1]
    
    # Direct match
    if clean_query in FIXED_ANSWERS:
        return FIXED_ANSWERS[clean_query]
    
    # Partial match for key phrases
    for key, answer in FIXED_ANSWERS.items():
        # Check if the key is a substantial part of the query
        if key in clean_query:
            return answer
        
        # Check for specific name mentions
        if "ajay saraswat" in clean_query and "ajay" in key:
            return FIXED_ANSWERS["ajay saraswat"]
        
        # Check for CEO questions
        if ("ceo" in clean_query or "chief executive" in clean_query) and "ceo" in key:
            return FIXED_ANSWERS["who is the ceo"]
            
        # Check for founder questions
        if ("founder" in clean_query or "founded" in clean_query) and "founder" in key:
            return FIXED_ANSWERS["who is the founder"]
            
        # Check for location questions
        if ("where" in clean_query or "location" in clean_query) and "location" in key:
            return FIXED_ANSWERS["where is the company located"]
            
        # Check for service questions
        if ("service" in clean_query or "what does" in clean_query) and "services" in key:
            return FIXED_ANSWERS["what services"]
    
    # No match found
    return None