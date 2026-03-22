from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QGroupBox, QSpinBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt

from modules.Settings import get_settings

def prettyPrint(msg: str):
    print("[SETTINGS_PAGE]:", msg)

class SettingsPageFrame(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
  
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout()

        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setMinimumWidth(50)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "Auto"))
        self.theme_combo.setMaximumWidth(200)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        appearance_layout.addLayout(theme_layout)
  
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)

        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.show_grid_check = QCheckBox("enable million dollar giver in ur bank account") # still tryna look for ideas for settings
        self.show_grid_check.setChecked(False)
        self.show_grid_check.stateChanged.connect(self.on_MONEYY)

        behavior_layout.addWidget(self.show_grid_check)
         
        behavior_group.setLayout(behavior_layout)
        main_layout.addWidget(behavior_group)
    
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout()
        
        about_text = QLabel(
            "Sibyl v2.0.0\n\n"
            "A Student Information System\n\n"
            "© 2026 - All rights reserved\n\n"
            "im larping psycho pass rn."
        )
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(about_text, alignment=Qt.AlignmentFlag.AlignBottom)
        
        about_group.setLayout(about_layout)
        main_layout.addWidget(about_group)
        
        main_layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("SelectionButton")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        main_layout.addLayout(button_layout)
    
    def on_theme_changed(self, theme: str):
       self.settings.set_theme(theme)
    
    def on_MONEYY(self, state):
        QMessageBox.information(None, "Title", f"MONEY {'YAY' if state else "NO!!"}")
  
    def on_show_grid_changed(self, state):
        self.settings.set("show_student_grid", self.show_grid_check.isChecked())
    
    def reset_to_defaults(self):
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.settings = self.settings.DEFAULT_SETTINGS.copy()
            self.settings.current_theme = self.settings._resolve_theme()
            self.settings.save_settings()
            
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentText(self.settings.get("theme", "Auto"))
            self.theme_combo.blockSignals(False)
            
            self.font_spinbox.setValue(self.settings.get("font_size", 10))
            self.auto_detect_check.setChecked(self.settings.get("auto_detect_theme", True))
            self.remember_size_check.setChecked(self.settings.get("remember_window_size", True))
            self.show_grid_check.setChecked(self.settings.get("show_student_grid", True))
            
            QMessageBox.information(self, "Success", "Settings have been reset to defaults.")
