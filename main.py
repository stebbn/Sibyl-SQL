"""
Sibyl - Student Information System
Manage student records, programs, and colleges with ease.
"""

import sys
import traceback
import time

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon

from modules.DataSQL import resource_path
from modules.utils import center_window, get_style, play_sound
from modules.Settings import get_settings

from ui import SidebarFrame
from ui.Pages import CollegeFinderFrame, DataPageFrame, SettingsPageFrame

def prettyPrint(msg: str):
    print("[Main]:", msg)

class SibylApp(QMainWindow):
    def __init__(self):
        super().__init__()
       
        self.settings = get_settings()
        config = self.settings.get_static()

        self.setWindowTitle(" ")
      
        self.setWindowIcon(QIcon(resource_path("ui/Assets/Logo.png")))
        self.setMinimumSize(config["window_width"], config["window_height"])
        
        center_window(self, config["window_width"], config["window_height"])
       
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 20, 0)
        layout.setSpacing(0)
      
        self.sidebar = SidebarFrame(on_nav_click=self.switch_page)
        layout.addWidget(self.sidebar)
        
        self.page_container = QWidget()
        self.page_container_layout = QHBoxLayout(self.page_container)
        self.page_container_layout.setContentsMargins(0, 0, 0, 0)
        self.page_container_layout.setSpacing(0)
        layout.addWidget(self.page_container, 1)
        
        self.ui_pages = {
            "College"   : CollegeFinderFrame,
            "Data"      : DataPageFrame,
            "Settings"  : SettingsPageFrame,
            "Stats"     : None
        }
        
        self.current_page = None
        self.current_page_name = ""
        self.starter_page = "Data"
      
        self.switch_page(self.starter_page)
        self.sidebar.update_selected(self.starter_page)
        
        self.settings.theme_changed.connect(self.apply_theme)
        
        prettyPrint("Application initialized")
    
    def switch_page(self, page_name: str):
        try:
            page_class = self.ui_pages.get(page_name)
            
            if page_class and self.current_page_name != page_name:
               
                while self.page_container_layout.count():
                    item = self.page_container_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                self.current_page = page_class()
                self.page_container_layout.addWidget(self.current_page)
                self.current_page_name = page_name
                
                play_sound(resource_path("ui/Assets/Sounds/button_click2.wav"))
                prettyPrint(f"Switched to {page_name}")
            else:
                if page_class:
                    prettyPrint(f"Page already displayed: {page_name}")
                else:
                    prettyPrint(f"Unable to switch to {page_name}")
                
        except Exception as e:
            prettyPrint(f"Error switching to {page_name}: {e}")
            traceback.print_exc()
    
    def apply_theme(self, theme_name: str = None):
        style = get_style()
        if style:
            QApplication.instance().setStyleSheet(style)
            prettyPrint(f"Theme applied: {self.settings.current_theme}")

def main():
    start_time = time.perf_counter()
    app = QApplication(sys.argv)

    app.setStyleSheet(get_style())

    window = SibylApp()
    window.show()
    play_sound(resource_path("ui/Assets/Sounds/sibyl_start.wav"))

    prettyPrint(f"Init load took {time.perf_counter() - start_time:.4f} seconds.")

    sys.exit(app.exec())

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == "__main__":
    sys.excepthook = except_hook
    main()

# longest 6.9624s