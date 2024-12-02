import cv2
import pytesseract
from PIL import Image

def capture_image():
    cam = cv2.VideoCapture(0)
    success, frame = cam.read()

    while True:
        _, image = cam.read()
        cv2.imshow('image', image)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite('test1.jpg', image)
            break
    cam.release()
    cv2.destroyAllWindows()

    return frame

def image_to_text():
    pytesseract.pytesseract.tesseract_cmd = r'D:\Programy\Tesseract\tesseract.exe'
    myconf = r"l pol+eng+deu+rus"
    image_path = "test1.jpg"
    text = pytesseract.image_to_string(Image.open(image_path), config=myconf)
    print(text)


if __name__ == "__main__":
    capture_image()
    image_to_text()