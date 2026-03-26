import pygame

from PIL import Image, ImageOps

from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication

from modules.Style import generate_stylesheet, get_theme

def processImage(file_loc, w, h, dark_mode_invert=False) -> QPixmap:
    og_img = Image.open(file_loc)
    
    if dark_mode_invert and get_theme() == "Light":
        r, g, b, a = og_img.split()
        inverted = ImageOps.invert(Image.merge('RGB', (r, g, b)))
        r2, g2, b2 = inverted.split()
        og_img = Image.merge('RGBA', (r2, g2, b2, a))
    
    og_img = og_img.resize((w, h), Image.Resampling.LANCZOS)
    data = og_img.tobytes("raw", "RGBA")
    q_img = QImage(data, w, h, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(q_img)

pygame.mixer.init() 
def play_sound(path, volume = 1):

    sound_effect = pygame.mixer.Sound(path)
    sound_effect.set_volume(volume)
    sound_effect.play()

def get_style() -> str:
    return generate_stylesheet()

def center_window(window, width, height) -> None:
    screen = QApplication.primaryScreen().geometry()
    x = (screen.width() - width) // 2
    y = (screen.height() - height) // 2
    window.setGeometry(x, y, width, height)