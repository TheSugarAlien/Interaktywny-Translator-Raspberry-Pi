# Interaktywny Translator Obraz-Tekst-Głos
## Działanie projektu
[Link do filmiku na Youtube](https://youtu.be/6-XtvUyeDUU)
## Krótki opis projektu
Celem naszego projektu było użycie dostępnego sprzętu domowego oraz wypożyczenie sprzętu 
laboratoryjnego, aby opracować projekt interaktywnego systemu tłumaczenia tekstu 
wykorzystującego kamerę internetową oraz API do tłumaczenia i syntezatora mowy. System 
pozwoli użytkownikowi uchwycić tekst z kartki papieru za pomocą kamery, wybrać język 
tłumaczenia za pomocą trzech dedykowanych przycisków, a następnie wyświetli przetłumaczony 
tekst na ekranie i odtworzy go za pomocą modułu syntezy mowy. Finalnie udało się zrobić system 
tłumaczenia tekstu z użyciem kamerki internetowej, możliwością akceptacji lub odrzucenia 
zdjęcia poprzez dwa dostępne przyciski, wyborem języka poprzez trzy dostępne przyciski, 
wyświetlanie każdego z kroków na wyświetlaczu i odtwarzanie przeczytanego tekstu za 
pośrednictwem głośnika. 
## Wykorzystany sprzęt
- Raspberry Pi 5
- Głośnik JBL XTREME
- Kamerka internetowa Tracer
- Wyświetlacz LCD Module ST7735S
- Breadboard z 5 przyciskami
## Wykorzystane technologie
- Python3
  - Pytesseract
  - OpenCV
  - GPIZERO (przyciski)
  - Pygame (dźwięk)
- API
  - DeepL
  - ElevenLabs
- Bluetooth
## Jak odtworzyć projekt
Aby odtworzyć ten projekt, trzeba:
1. Odbudować go przy pomocy schematu podanego w pliku Sprawozdanie.pdf
2. Stworzyć plik .env, w którym trzeba zawrzeć potrzebne klucze prywatne do API DeepL, ElevenLabs oraz ID do konkretnych głosów syntezy mowy
3. Zgrać pliki Main.py, requirements.txt oraz .env do pamięci Raspberry Pi 5
4. Stworzyć wirtualne środowisko Python3
5. Zainstalować w nim wszystkie potrzebne biblioteki (np. ```pip install -r requirements.txt```)
6. Odpalić plik Main.py


