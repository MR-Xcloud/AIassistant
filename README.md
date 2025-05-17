# Voice Assistant with Azure Speech Services

This project implements a voice assistant that can answer questions using data scraped from a website. It uses Azure Speech Services for speech-to-text and text-to-speech capabilities.

## Features

- Voice input using Azure Speech-to-Text
- Voice output using Azure Text-to-Speech
- Semantic search on website content
- Web scraping and content indexing

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure your Azure Speech Service credentials are set in the `.env` file:
   ```
   AZURE_SPEECH_KEY=your_key_here
   AZURE_SPEECH_REGION=your_region_here
   ```

3. Run the voice assistant:
   ```
   python voice_assistant.py
   ```

## Usage

1. When the voice assistant starts, it will greet you.
2. Speak your question clearly into your microphone.
3. The assistant will process your question, search for relevant information, and respond with an answer.
4. To exit, say "goodbye", "exit", or "quit".

## Components

- `voice_assistant.py`: Main voice assistant implementation using Azure Speech Services
- `chatbot.py`: Web scraping and semantic search functionality
- `.env`: Configuration file for Azure credentials
- `requirements.txt`: List of required Python packages

## Troubleshooting

- Make sure your microphone is properly connected and set as the default input device
- Check that your Azure Speech Service key and region are correct
- If you encounter issues with web scraping, try running `chatbot.py` directly first to build the cache