import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

deepl_api_key = os.getenv('DEEPL_API_KEY')


def translate_text(text, target_language):
    url = "https://api-free.deepl.com/v2/translate"

    params = {
        'auth_key': deepl_api_key,
        'text': text,
        'target_lang': target_language
    }

    response = requests.post(url, data=params)

    if response.status_code == 200:
        translation_result = response.json()['translations'][0]
        translated_text = translation_result['text']
        detected_source_language = translation_result['detected_source_language']
        return translated_text, detected_source_language
    else:
        raise Exception(f"Error: {response.status_code}, Message: {response.text}")


def detect_language(text):
    _, detected_source_language = translate_text(text, 'EN')
    return detected_source_language


available_languages = {
    'PL': {'ENG': 'en', 'RU': 'ru', 'DE': 'de'},
    'EN': {'PL': 'pl', 'RU': 'ru', 'DE': 'de'},
    'RU': {'PL': 'pl', 'ENG': 'en', 'DE': 'de'},
    'DE': {'PL': 'pl', 'ENG': 'en', 'RU': 'ru'}
}


def main():
    #Ten tekst da nam OCR
    input_text = "Witaj, świecie! Nazywam się Mateusz!"

    detected_language = detect_language(input_text).upper()
    print(f"Język tekstu to: {detected_language}")

    if detected_language not in available_languages:
        print(f"Niewspierany język: {detected_language}")
        sys.exit(1)

    #Język docelowy będzie wybierany przy pomocy przycisków
    target_language_code = input(
        f"Na jaki język przetłumaczyć? {list(available_languages[detected_language].keys())}: ").upper()

    target_language = available_languages[detected_language].get(target_language_code)

    if target_language:
        translated_text, _ = translate_text(input_text, target_language)
        print(f"Przetłumaczony tekst: {translated_text}")


if __name__ == "__main__":
    main()
