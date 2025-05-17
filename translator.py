"""
Translator module for translating text between languages.
Uses Azure Translator service for high-quality translations.
"""

import requests
import uuid
import json

# Azure Translator credentials - using the same key as Speech Service
AZURE_TRANSLATOR_KEY = "9mN5lzQidMfporvrWZ494iDmaig34WouPBsYnr98RsQlmGdf9Q39JQQJ99BEACYeBjFXJ3w3AAAYACOGhEFF"
AZURE_TRANSLATOR_REGION = "eastus"
AZURE_TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

def translate_text(text, to_language="hi", from_language="en"):
    """
    Translate text to the specified language using Azure Translator.
    
    Args:
        text (str): The text to translate
        to_language (str): The target language code (default: 'hi' for Hindi)
        from_language (str): The source language code (default: 'en' for English)
        
    Returns:
        str: The translated text, or the original text if translation fails
    """
    try:
        # Construct the request URL
        path = '/translate'
        constructed_url = AZURE_TRANSLATOR_ENDPOINT + path
        
        # Set up the request parameters
        params = {
            'api-version': '3.0',
            'from': from_language,
            'to': to_language
        }
        
        # Set up the request headers
        headers = {
            'Ocp-Apim-Subscription-Key': AZURE_TRANSLATOR_KEY,
            'Ocp-Apim-Subscription-Region': AZURE_TRANSLATOR_REGION,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
        
        # Create the request body
        body = [{
            'text': text
        }]
        
        # Make the request
        response = requests.post(constructed_url, params=params, headers=headers, json=body)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response
        result = response.json()
        
        # Extract the translated text
        if result and len(result) > 0:
            translations = result[0].get('translations', [])
            if translations and len(translations) > 0:
                return translations[0].get('text', text)
        
        return text  # Return original text if translation extraction fails
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails