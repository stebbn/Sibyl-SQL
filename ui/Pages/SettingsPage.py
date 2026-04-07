from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QPushButton, QGroupBox, QSpinBox, QCheckBox, QMessageBox, QSlider)
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
        theme_label = QLabel("Preferrence:")
        theme_label.setMinimumWidth(50)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Dark", "Light"])
        self.theme_combo.setMaximumWidth(200)
        
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)

        theme_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)

        page_layout = QHBoxLayout()
        psize_label = QLabel("Page Rows Size:")
        psize_label.setMinimumWidth(50)

        self.page_size = QSpinBox(self)
        self.page_size.setRange(5, 200)
        self.page_size.setSingleStep(1)
        self.page_size.setMaximumHeight(35)
        self.page_size.setMaximumWidth(100)

        self.page_size.valueChanged.connect(self.on_page_size_changed)

        page_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        page_layout.addWidget(psize_label)
        page_layout.addWidget(self.page_size)

        sound_layout = QHBoxLayout()
        vol_label = QLabel("Volume:")
        vol_label.setMinimumWidth(50)

        self.vol_number = QLabel("0%")
        self.vol_number.setMinimumWidth(40)
        self.vol_number.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0,100)
        self.volume.setMaximumWidth(250)

        self.volume.valueChanged.connect(self.on_volume_changed)

        sound_layout.addWidget(vol_label)
        sound_layout.addWidget(self.vol_number)
        sound_layout.addWidget(self.volume)
        
        sound_layout.addStretch()
        sound_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
       
        appearance_layout.addLayout(theme_layout)
        appearance_layout.addLayout(page_layout)
        appearance_layout.addLayout(sound_layout)
  
        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)

        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout()

        self.show_grid_check = QCheckBox("Remember Last Page") 
        self.show_grid_check.checkStateChanged.connect(self.on_save_page)

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

        self.setup_default_settings()

        main_layout.addLayout(button_layout)

    def setup_default_settings(self):
        self.theme_combo.setCurrentText(self.settings.get("theme"))
        self.page_size.setValue(self.settings.get("page_content_size"))
        self.volume.setValue(self.settings.get("sound_volume"))
        self.show_grid_check.setChecked(self.settings.get("remember_last_page"))
    
    def on_theme_changed(self, theme: str):
       self.settings.set_theme(theme)
    
    def on_volume_changed(self, value):
        self.settings.set("sound_volume", value)
        self.vol_number.setText(f"{self.volume.value()}%")
    
    def on_save_page(self, state):
        self.settings.set("remember_last_page", Qt.CheckState.Checked == state)

    def on_page_size_changed(self, value):
        self.settings.set("page_content_size", value)
  
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
            
            self.setup_default_settings()
            
            QMessageBox.information(self, "Success", "Settings have been reset to defaults.")