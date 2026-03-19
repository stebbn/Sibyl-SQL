import json
import os
import darkdetect

from PyQt6.QtCore import QObject, pyqtSignal

from typing import Any, Dict
from modules.Data import resource_path

def prettyPrint(msg):
    print("[SETTINGS]:", msg)

class SettingsManager(QObject):
  
    # Events
    theme_changed = pyqtSignal(str)

    STATIC_SETTINGS = {
        "window_width": 1250,
        "window_height": 700,
    }

    DEFAULT_SETTINGS = {
        "theme": "Auto",  # Auto, Dark, Light
        "auto_detect_theme": True,
        "remember_window_size": True,
        "language": "English",
        "font_size": 10,
        "show_student_grid": True,
    }
    
    THEME_COLORS = {
        "Dark": {
            "background": "#131212",
            "foreground": "#313131",
            "accent": "rgba(100, 200, 255, 100)",
            "secondary_bg": "#181717",
            "border": "#404040",
        },
        "Light": {
            "background": "#ECECEC",
            "foreground": "#CECECE",
            "accent": "rgba(70, 150, 220, 100)",
            "secondary_bg": "#F5F5F5",
            "border": "#D0D0D0",
        }
    }
    
    def __init__(self):
        super().__init__()

        self.config_path = self._get_config_path()
        self.settings = self._load_settings()
        self.current_theme = self._resolve_theme()

        prettyPrint(f"Settings loaded from {self.config_path}")
        prettyPrint(f"Current theme: {self.current_theme}")
    
    def _get_config_path(self) -> str:
        return resource_path("data/settings.json")
    
    def _load_settings(self) -> Dict[str, Any]:
        if self.config_path:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return {**self.DEFAULT_SETTINGS, **loaded}
            except Exception as e:
                prettyPrint(f"Error loading settings: {e}, using defaults")
                return self.DEFAULT_SETTINGS.copy()
        return self.DEFAULT_SETTINGS.copy()
    
    def _resolve_theme(self) -> str:
        if self.settings["theme"] == "Auto":
            system_theme = "Dark" if darkdetect.theme() == "Dark" else "Light"
            return system_theme
        return self.settings["theme"]
    
    def save_settings(self) -> bool:
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            prettyPrint("Settings saved successfully")
            return True
        except Exception as e:
            prettyPrint(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save_settings()
    
    def set_theme(self, theme: str) -> bool:
        if theme not in ["Auto", "Dark", "Light"]:
            prettyPrint(f"Invalid theme: {theme}")
            return False
        
        old_theme = self.current_theme
        self.settings["theme"] = theme
        self.current_theme = self._resolve_theme()
        self.save_settings()
        
        changed = old_theme != self.current_theme

        if changed:
            prettyPrint(f"Theme changed from {old_theme} to {self.current_theme}")
            self.theme_changed.emit(f"{self.current_theme}")
        return changed
    
    def get_colors(self) -> Dict[str, str]:
        return self.THEME_COLORS.get(self.current_theme, self.THEME_COLORS[self._resolve_theme()])

    def get_static(self):
        return self.STATIC_SETTINGS

    def get_all_settings(self) -> Dict[str, Any]:
        return self.settings.copy()

_settings_instance = None

def get_settings() -> SettingsManager:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SettingsManager()
    return _settings_instance
