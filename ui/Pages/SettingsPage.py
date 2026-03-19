from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QGroupBox, QSpinBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
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
        theme_label.setMinimumWidth(150)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "Auto"))
        self.theme_combo.setMaximumWidth(200)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
  
        font_layout = QHBoxLayout()
        font_label = QLabel("Font Size:")
        font_label.setMinimumWidth(150)
        self.font_spinbox = QSpinBox()
        self.font_spinbox.setMinimum(8)
        self.font_spinbox.setMaximum(16)
        self.font_spinbox.setValue(self.settings.get("font_size", 10))
        self.font_spinbox.setMaximumWidth(100)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_spinbox)
        font_layout.addStretch()
        
        appearance_layout.addLayout(font_layout)
        
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)

        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.auto_detect_check = QCheckBox("Auto-detect system theme (when theme is set to Auto)")
        self.auto_detect_check.setChecked(self.settings.get("auto_detect_theme", True))
        self.auto_detect_check.stateChanged.connect(self.on_auto_detect_changed)
        behavior_layout.addWidget(self.auto_detect_check)

        self.remember_size_check = QCheckBox("Remember window size and position")
        self.remember_size_check.setChecked(self.settings.get("remember_window_size", True))
        self.remember_size_check.stateChanged.connect(self.on_remember_size_changed)
        behavior_layout.addWidget(self.remember_size_check)
 
        self.show_grid_check = QCheckBox("Show student data as grid")
        self.show_grid_check.setChecked(self.settings.get("show_student_grid", True))
        self.show_grid_check.stateChanged.connect(self.on_show_grid_changed)
        behavior_layout.addWidget(self.show_grid_check)
        
        behavior_group.setLayout(behavior_layout)
        main_layout.addWidget(behavior_group)
    
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout()
        
        about_text = QLabel(
            "Sibyl v1.0.0\n\n"
            "A Student Information System\n\n"
            "© 2026 - All rights reserved\n\n"
            "im larping psycho pass rn."
        )
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(about_text)
        
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
    
    def on_auto_detect_changed(self, state):
        self.settings.set("auto_detect_theme", self.auto_detect_check.isChecked())
    
    def on_remember_size_changed(self, state):
        self.settings.set("remember_window_size", self.remember_size_check.isChecked())
    
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
