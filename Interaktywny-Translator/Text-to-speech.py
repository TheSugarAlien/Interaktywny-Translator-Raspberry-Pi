from Translator import main
import os
from dotenv import load_dotenv
import requests

load_dotenv()

elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

text, language = main()

voice_ids = {
    'en': os.getenv("ENGLISH_ID"),
    'pl' : os.getenv("POLISH_ID"),
    'ru': os.getenv("RUSSIAN_ID"),
    'de': os.getenv("GERMAN_ID")
}

CHUNK_SIZE = 1024
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_ids[language]}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": elevenlabs_api_key
}

data = {
    "text": text,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.75,
        "similarity_boost": 0.85
    }
}

response = requests.post(url, json=data, headers=headers)
with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)