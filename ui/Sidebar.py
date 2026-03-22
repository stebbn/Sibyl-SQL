from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QColor, QIcon

from modules.DataSQL import resource_path
from modules.utils import processImage
from modules.Settings import get_settings

import modules.DataSQL as data

def prettyPrint(msg: str): 
    print("[SIDEBAR]:", msg)

class SidebarFrame(QFrame):
    def __init__(self, on_nav_click):
        super().__init__()
        
        self.setObjectName("SidebarFrame")
        self.on_nav_click = on_nav_click
        self.nav_buttons = {}
        self.current_button = None

        self.settings = get_settings()

        self.OpenAnim = QPropertyAnimation(self, b"maximumWidth")
        self.OpenAnim.setDuration(800)

        self.OpenAnim.setStartValue(0)
        self.OpenAnim.setEndValue(160)

        self.OpenAnim.setEasingCurve(QEasingCurve.Type.OutCirc)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 30, 10, 10)
        self.layout.setSpacing(5)
     
        self.icon_image = processImage(resource_path("ui/Assets/Logo.png"), 120, 120)
        logo_lbl = QLabel()
        logo_lbl.setPixmap(self.icon_image)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setObjectName("LogoLabel")
        self.layout.addWidget(logo_lbl)

        self.get_icons()
        self.settings.theme_changed.connect(self.update_icons)

        self.create_button("Data", "Data")
        self.create_button("Colleges", "College")
        self.create_button("Stats", "Stats")

        spacer = QLabel()
        self.layout.addStretch()
     
        self.create_button("Settings", "Settings")
     
        info_lbl = QLabel("To create and manage.")
        info_lbl.setObjectName("InfoLabel")
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(info_lbl)
        
        self.OpenAnim.start()

    def get_icons(self):
        self.icons = {
            "College"  : processImage(resource_path("ui/Assets/college.png"), 26, 26, dark_mode_invert=True),
            "Data"     : processImage(resource_path("ui/Assets/database.png"), 26, 26, dark_mode_invert=True),
            "Settings" : processImage(resource_path("ui/Assets/setting.png"), 26, 26, dark_mode_invert=True),
            "Stats"    : processImage(resource_path("ui/Assets/stats.png"), 26, 26, dark_mode_invert=True),
        }
    
    def update_icons(self):
        self.get_icons()

        for item in self.icons:
            if not self.nav_buttons.get(item): continue 

            self.nav_buttons[item].setIcon(QIcon(self.icons.get(item)))

    def create_button(self, name: str, call_name: str):
        btn = QPushButton()
        btn.setText(f"   {name}")
        
        image_pixmap = self.icons[call_name]

        if image_pixmap:
            icon = QIcon(image_pixmap)
            btn.setIcon(icon)
            btn.setIconSize(image_pixmap.rect().size())
        
        btn.clicked.connect(lambda: self.handle_click(btn, call_name))
        self.nav_buttons[call_name] = btn

        self.layout.addWidget(btn)
            
    def update_selected(self, new: str):
        old_button = self.current_button
        the_button = self.nav_buttons.get(new)
        
        self.current_button = the_button
        
        if old_button:
            old_button.setProperty("selected", False)
            old_button.style().unpolish(old_button)
            old_button.style().polish(old_button)
        
        if the_button:
            the_button.setProperty("selected", True)
            the_button.style().unpolish(the_button)
            the_button.style().polish(the_button)
        else:
            prettyPrint(f"invalid button update {new}")
            prettyPrint(self.nav_buttons)
    
    def handle_click(self, btn: QPushButton, page_name: str):
        self.update_selected(page_name)
        self.on_nav_click(page_name)


        