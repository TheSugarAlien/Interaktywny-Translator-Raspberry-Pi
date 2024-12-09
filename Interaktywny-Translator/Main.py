import cv2
import pytesseract
from PIL import Image
from dotenv import load_dotenv
import os
import sys
import requests

load_dotenv()

tesseract_path = os.getenv('TESSERACT')
deepl_api_key = os.getenv('DEEPL_API_KEY')
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')

voice_ids = {
    'en': os.getenv("ENGLISH_ID"),
    'pl': os.getenv("POLISH_ID"),
    'ru': os.getenv("RUSSIAN_ID"),
    'de': os.getenv("GERMAN_ID")
}

CHUNK_SIZE = 1024


def preprocess_image(image_path):
    """Preprocess the image for better OCR."""
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    denoised = cv2.medianBlur(binary, 3)

    processed_path = "test1.jpg"
    cv2.imwrite(processed_path, denoised)

    return processed_path

def capture_image():
    """Capture an image using the webcam."""
    cam = cv2.VideoCapture(0)
    success, frame = cam.read()

    while True:
        _, image = cam.read()
        cv2.imshow('image', image)
        key = cv2.waitKey(0) & 0xFF
        if key == ord("s"):
            print("Saving image...")
            cv2.imwrite("test1.jpg",frame)
            break
        elif key == ord("r"):
            print("Retaking image...")
            continue


    cam.release()
    cv2.destroyAllWindows()

    return frame


def image_to_text():
    """Convert an image to text using Tesseract OCR."""
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    myconf = r"-l pol+eng+deu+rus"

    # Preprocess the image
    processed_path = preprocess_image("test1.jpg")

    # Perform OCR
    text = pytesseract.image_to_string(Image.open(processed_path), config=myconf)
    print(f"Extracted text: {text}")

    # Ask the user if the text is correct
    is_clear = input("Is this the text? (y/n) ")
    if is_clear == "n":
        capture_image()
        image_to_text()

    return text


def translate_text(text, target_language):
    """Translate text using the DeepL API."""
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
    """Detect the language of a given text."""
    _, detected_source_language = translate_text(text, 'EN')
    return detected_source_language


def text_to_speech(text, language):
    """Convert text to speech using the ElevenLabs API."""
    voice_id = voice_ids.get(language)

    if not voice_id:
        raise ValueError(f"Voice ID for language '{language}' not found!")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
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
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, Message: {response.text}")

    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    print("Audio saved as 'output.mp3'")


available_languages = {
    'PL': {'ENG': 'en', 'RU': 'ru', 'DE': 'de'},
    'EN': {'PL': 'pl', 'RU': 'ru', 'DE': 'de'},
    'RU': {'PL': 'pl', 'ENG': 'en', 'DE': 'de'},
    'DE': {'PL': 'pl', 'ENG': 'en', 'RU': 'ru'}
}


def main():
    # Step 1
    print("Capturing image...")
    capture_image()
    input_text = image_to_text()

    # Step 2
    detected_language = detect_language(input_text).upper()
    print(f"Detected language: {detected_language}")

    if detected_language not in available_languages:
        print(f"Unsupported language: {detected_language}")
        sys.exit(1)

    # Step 3
    target_language_code = input(
        f"Translate to which language? {list(available_languages[detected_language].keys())}: ").upper()

    target_language = available_languages[detected_language].get(target_language_code)

    if not target_language:
        print(f"Invalid target language: {target_language_code}")
        sys.exit(1)

    translated_text, _ = translate_text(input_text, target_language)
    print(f"Translated text: {translated_text}")

    # Step 4
    text_to_speech(translated_text, target_language)


if __name__ == "__main__":
    main()
