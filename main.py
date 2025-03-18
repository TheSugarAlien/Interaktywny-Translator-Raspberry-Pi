from gpiozero import Button
from signal import pause
import cv2
import pytesseract
from dotenv import load_dotenv
import os
import sys
import requests
import board
import busio
from RPLCD.i2c import CharLCD
from time import sleep
from elevenlabs import ElevenLabs
import pygame
import time
import re
import time
import spidev as SPI
sys.path.append("..")
from lib import LCD_1inch8
from PIL import Image,ImageDraw,ImageFont
import textwrap

RST = 27
DC = 25
BL = 18
bus = 0
device = 0

disp = LCD_1inch8.LCD_1inch8(spi=SPI.SpiDev(bus, device), spi_freq=10000000, rst=RST, dc=DC, bl=BL)

disp.Init()
disp.clear()
disp.bl_DutyCycle(50)

def display_text_to_lcd(text):
	'''Wyświetlanie tekstu na wyświetlaczu lcd'''
    try:
        disp.clear()

        image1 = Image.new("RGB", (disp.width, disp.height), "BLUE")
        draw = ImageDraw.Draw(image1)

        Font2 = ImageFont.truetype("../Font/Font00.ttf", 10)

        max_chars_per_line = 30
        line_height = 14

        manual_lines = text.split('\n')

        wrapped_lines = []
        for line in manual_lines:
            if line.strip() == "":
                wrapped_lines.append("")
            else:
                wrapped_part = textwrap.wrap(
                    line,
                    width=max_chars_per_line,
                    break_long_words=False,
                    break_on_hyphens=False
                )
                if not wrapped_part:
                    wrapped_lines.append("")
                else:
                    wrapped_lines.extend(wrapped_part)


        for i, line in enumerate(wrapped_lines):
            draw.text((1, 1 + i * line_height), line, font=Font2, fill="WHITE")

        disp.ShowImage(image1)
        time.sleep(2)

pygame.mixer.init()

GPIO_PIN_CZERWONY = 9
GPIO_PIN_ZIELONY = 22
GPIO_PIN_1 = 26
GPIO_PIN_2 = 17
GPIO_PIN_3 = 23

button_czerwony = Button(GPIO_PIN_CZERWONY, pull_up=True)
button_ziolony = Button(GPIO_PIN_ZIELONY, pull_up=True)
button_1 = Button(GPIO_PIN_1, pull_up=True)
button_2 = Button(GPIO_PIN_2, pull_up=True)
button_3 = Button(GPIO_PIN_3, pull_up=True)

load_dotenv()

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
    """Przetwarzanie obrazu do OCR."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    denoised = cv2.medianBlur(binary, 3)
    processed_path = "processed.jpg"
    cv2.imwrite(processed_path, denoised)
    return processed_path


def capture_image():
    """Robienie zdjęcia za pomocą kamery."""
    cam = cv2.VideoCapture(0)
    display_text_to_lcd("Przechwytywanie zdjęcia...")
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("captured.jpg", frame)
        display_text_to_lcd("Zdjęcie zapisane!")

    else:
        display_text_to_lcd("Brak zdjęcia!")
    cam.release()


def image_to_text():
    """Konwersja obrazu na tekst za pomocą OCR."""
    myconf = r"-l pol+eng+deu+rus"
    display_text_to_lcd("Wyciąganie tekstu ze zdjęcia...")
    text = pytesseract.image_to_string(Image.open("captured.jpg"), config=myconf)
    display_text_to_lcd("Tekst wyciągnięty!")
    text = re.sub(r'[^\x20-\x7E]+', '', text)
    text = text.strip()
    print(f"Extracted text: {text}")
    return text


def translate_text(text, target_language):
    """Tłumaczenie tekstu za pomocą API DeepL."""
    display_text_to_lcd("Tłumaczenie tekstu...")
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
        raise Exception(f"Translation error: {response.status_code}")


def text_to_speech(text, language, elevenlabs_api_key, voice_ids):
    """Syntezowanie mowy z tekstu za pomocą ElevenLabs."""
    if not text:
        raise ValueError("Text cannot be empty or None")

    text = str(text)
    print(f"Text type: {type(text)}")

    display_text_to_lcd("Generowanie audio...")

    voice_id = voice_ids.get(language)
    if not voice_id:
        raise ValueError(f"Voice ID for language '{language}' not found!")

    print(f"Using voice ID: {voice_id}")

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
    print(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        with open('output.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        print(f"Error: {response.status_code}, {response.text}")
        raise Exception(f"Error: {response.status_code} - {response.text}")


def play_audio(audio: str):
    '''Inicjalizacja miksera Pygame'''
    mp3_file = audio
    pygame.mixer.music.load(mp3_file)

    print("Odtwarzanie pliku MP3 na głośniku Bluetooth...")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)

    print("Odtwarzanie zakończone.")


def detect_language(text):
    """Detekcja języka tekstu."""
    display_text_to_lcd("Szukanie języka tekstu...")
    _, detected_language = translate_text(text, 'EN')
    return detected_language


available_languages = {
    'PL': {'ENG': 'en', 'RU': 'ru', 'DE': 'de'},
    'EN': {'PL': 'pl', 'RU': 'ru', 'DE': 'de'},
    'RU': {'PL': 'pl', 'ENG': 'en', 'DE': 'de'},
    'DE': {'PL': 'pl', 'ENG': 'en', 'RU': 'ru'}
}


def button_callback(channel):
    if channel == GPIO_PIN_ZIELONY:
        accepted = True
    elif channel == GPIO_PIN_CZERWONY:
        accepted = False


global accepted


def main():
    # Step 1: Robienie zdjęcia
    display_text_to_lcd("Start")
    button_ziolony_pressed = False
    button_czerwony_pressed = False

    while True:
        print("ROBIMY ZDJ")
        capture_image()
        print("ZDJ NA TEXT")
        input_text = image_to_text()
        display_text_to_lcd(f"{input_text}")

        print("Czy zdjecie sie podoba? Z/C")

        while True:
            time.sleep(0.1)  # Krótkie opóźnienie, aby nie obciążać procesora

            # Sprawdzamy stan przycisku zielonego
            if button_ziolony.is_pressed and not button_ziolony_pressed:
                print("Zdjęcie zaakceptowane!")
                button_ziolony_pressed = True  # Ustawiamy flagę, aby zapobiec wielokrotnemu kliknięciu
                break  # Akceptacja zdjęcia, wychodzimy z pętli pytania

            # Sprawdzamy stan przycisku czerwonego
            if button_czerwony.is_pressed and not button_czerwony_pressed:
                print("Zdjęcie odrzucone. Powtarzamy.")
                time.sleep(0.5)  # Unikamy zbyt szybkiego wielokrotnego wyzwolenia
                button_czerwony_pressed = True  # Ustawiamy flagę, aby zapobiec wielokrotnemu kliknięciu
                break  # Powtarzamy wykonanie zdjęcia

        # Resetujemy flagi, aby umożliwić kolejne naciśnięcie przycisków
        if not button_ziolony.is_pressed:
            button_ziolony_pressed = False
        if not button_czerwony.is_pressed:
            button_czerwony_pressed = False

        # Sprawdzamy, czy zdjęcie zostało zaakceptowane
        if button_ziolony.is_pressed:
            break  # Przerywamy główną pętlę po akceptacji zdjęcia

    # Step 3: Detekcja języka
    detected_language = detect_language(input_text).upper()
    print(f"Detected language: {detected_language}")
    display_text_to_lcd(f"Język tekstu: {detected_language}")

    if detected_language not in available_languages:
        display_text_to_lcd("Język nie jest wspierany przez program.")
        sys.exit(1)

    possible_languages = list(available_languages[detected_language].keys())

    display_text_to_lcd(f"Na jaki język chcesz przetłumaczyć tekst?\n\n1.{possible_languages[0]} 2.{possible_languages[1]} 3.{possible_languages[2]}")
    while True:
        if button_1.is_pressed:
            target_language_code = possible_languages[0]
            break  # Przerywamy pętlę po przypisaniu wartości

        if button_2.is_pressed:
            target_language_code = possible_languages[1]
            break  # Przerywamy pętlę po przypisaniu wartości

        if button_3.is_pressed:
            target_language_code = possible_languages[2]
            break  # Przerywamy pętlę po przypisaniu wartości

        time.sleep(0.1)

    target_language = available_languages[detected_language].get(target_language_code)

    # Step 5: Tłumaczenie
    translated_text = translate_text(input_text, target_language)
    print(f"Translated text: {translated_text[0]}")


    # Step 6: Generowanie mowy
    text_to_speech(translated_text[0], target_language, elevenlabs_api_key, voice_ids)
    display_text_to_lcd(translated_text[0])
    play_audio("output.mp3")
    time.sleep(10)



if __name__ == "__main__":
    main()
