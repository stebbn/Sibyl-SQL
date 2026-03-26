from modules.Settings import get_settings

def get_theme():
    return get_settings().current_theme

def generate_stylesheet():
    settings = get_settings()
    colors   = settings.get_colors()
 
    bg              = colors["background"]
    secondary_bg    = colors["secondary_bg"]
    fg              = colors["foreground"]
    accent          = colors["accent"]
    border          = colors["border"]
  
    is_dark         = settings.current_theme == "Dark"
    text_color      = "#FFFFFF" if is_dark else "#1A1919"
    secondary_text  = "#050303" if is_dark else "#555555"
    
    stylesheet = f"""

/* ----------------------- MAIN WINDOW ----------------------- */
QMainWindow {{
    background-color: {bg};
    color: {text_color};
}}

QWidget {{
    background-color: {bg};
    color: {text_color};
}}

/* ----------------------- SIDEBAR ----------------------- */
QFrame {{
    background-color: {bg};
    border: none;
}}

#SidebarFrame {{
    background-color: {secondary_bg};
    border: none;
}}

#LogoLabel {{ 
    color: {secondary_bg};
    background-color:{secondary_bg};
    padding: 10px;
}}

#InfoLabel {{
    font-size: 7pt;
    font-style: italic;
    color: {text_color};
    background-color:{secondary_bg};
}}

/* ----------------------- BUTTONS ----------------------- */
QPushButton {{
    background-color: transparent;
    border: none;
    padding: 8px;
    text-align: left;
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
    font-weight: 500;
    outline: none;
    border-radius: 4px;

    margin-bottom: 15px;

}}

QPushButton:hover {{
    background-color: rgba(100, 200, 255, 0.15);
}}

QPushButton:pressed {{
    background-color: rgba(100, 200, 255, 0.3);
}}

QPushButton[selected="true"] {{
    background-color: rgba(100, 200, 255, 0.3);
    color: {text_color};
}}

QPushButton[selected="true"]:hover {{
    background-color: rgba(100, 200, 255, 0.4);
}}

/* selections */ 

#SelectionButton{{
    background-color: {fg};
}}
#SelectionButton:hover {{ background-color: rgba(100, 200, 255, 0.15); }}
#SelectionButton[selected="true"] {{ background-color: rgba(100, 200, 255, 0.3); }}
#SelectionButton:checked {{
                background-color: rgba(100, 200, 255, 0.3); 
                font-weight: bold; 
            }}

/* ----------------------- INPUT FIELDS ----------------------- */
QLineEdit {{
    background-color: {secondary_bg};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 6px;
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
    selection-background-color: rgba(100, 200, 255, 0.4);
}}

QLineEdit:focus {{
    border: 2px solid rgba(100, 200, 255, 0.8);
    padding: 5px;
}}

QComboBox {{
    background-color: {secondary_bg};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 6px;
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
}}

QComboBox:focus {{
    border: 2px solid rgba(100, 200, 255, 0.8);
    padding: 5px;
}}

QComboBox::drop-down {{
    border: none;
    background-color: transparent;
}}

QComboBox::down-arrow {{
    image: none;
    border: none;
    width: 16px;
    height: 16px;
}}

QComboBox QAbstractItemView {{
    background-color: {secondary_bg};
    color: {text_color};
    selection-background-color: rgba(100, 200, 255, 0.4);
    border: 1px solid {border};
}}

QSpinBox {{
    background-color: {secondary_bg};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 6px;
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
}}

QSpinBox:focus {{
    border: 2px solid rgba(100, 200, 255, 0.8);
    padding: 5px;
}}

QSpinBox::up-button {{
    width: 25px;
}}

QSpinBox::down-button {{
    width: 25px;
}}

/* ----------------------- LABELS ----------------------- */
QLabel {{
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
}}

#FormTitle {{
    font-size: 12pt;
    font-weight: bold;
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
}}

QLabel[status="error"] {{
    color: #FF6B6B;
}}

QLabel[status="success"] {{
    color: #18C421;
}}

QLabel[status="warning"] {{
    color: #FFDC6B;
}}

/* ----------------------- TEXT EDIT / DISPLAY BOXES ----------------------- */
QTextEdit {{
    background-color: {bg};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 6px;
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
}}

QTextEdit:focus {{
    border: 2px solid rgba(100, 200, 255, 0.8);
    padding: 5px;
}}

/* ----------------------- CHECKBOXES ----------------------- */
QCheckBox {{
    color: {text_color};
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

QCheckBox::indicator:unchecked {{
    background-color: {secondary_bg};
    border: 1px solid {border};
    border-radius: 3px;
}}

QCheckBox::indicator:checked {{
    background-color: rgba(100, 200, 255, 0.6);
    border: 1px solid rgba(100, 200, 255, 0.8);
    border-radius: 3px;
}}

QCheckBox::indicator:hover {{
    border: 1px solid rgba(100, 200, 255, 0.8);
}}

/* ----------------------- TABLES ----------------------- */
QTableWidget {{
    background-color: {secondary_bg};
    alternate-background-color: {bg};
    gridline-color: {border};
    border: 1px solid {border};
    border-radius: 4px;
    color: {text_color};
}}

QTableWidget::item {{
    padding: 4px;
    color: {text_color};
}}

QTableWidget::item:selected {{
    color: {text_color};
}}

QHeaderView::section {{
    background-color: {bg};
    color: {text_color};
    padding: 6px;
    border: none;
    border-bottom: 1px solid {border};
    font-weight: bold;
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
}}

/* ----------------------- TABS ----------------------- */
QTabWidget {{
    background-color: {bg};
    color: {text_color};
    border: none;
}}

QTabBar::tab {{
    background-color: {secondary_bg};
    color: {text_color};
    padding: 8px 16px;
    margin: 0px 2px;
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
    border-bottom: 2px solid {border};
}}

QTabBar::tab:selected {{
    background-color: {bg};
    border-bottom: 2px solid rgba(100, 200, 255, 0.8);
    color: {text_color};
}}

QTabBar::tab:hover {{
    background-color: {border};
}}

QTabWidget::pane {{
    border: none;
}}

/* ----------------------- SCROLL BARS ----------------------- */
QScrollBar:vertical {{
    background-color: {bg};
    width: 12px;
    border: none;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {border};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: rgba(100, 200, 255, 0.6);
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {bg};
    height: 12px;
    border: none;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {border};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: rgba(100, 200, 255, 0.6);
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
}}

/* ----------------------- MENUS ----------------------- */
QMenu {{
    background-color: {secondary_bg};
    color: {text_color};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 4px;
}}

QMenu::item:selected {{
    background-color: rgba(100, 200, 255, 0.4);
    color: {text_color};
    border-radius: 3px;
}}

QMenu::item:pressed {{
    background-color: rgba(100, 200, 255, 0.6);
}}

QMenu::separator {{
    height: 1px;
    background-color: {border};
    margin: 4px 0px;
}}

/* ----------------------- DIALOGS ----------------------- */
QDialog {{
    background-color: {bg};
    color: {text_color};
}}

QMessageBox {{
    background-color: {bg};
}}

QMessageBox QLabel {{
    color: {text_color};
}}

QMessageBox QPushButton {{
    min-width: 60px;
    min-height: 24px;
}}

/* ----------------------- GROUPBOX ----------------------- */
QGroupBox {{
    color: {text_color};
    border: 1px solid {border};
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 10px;
    font-family: 'Bahnschrift SemiLight';
    font-size: 10pt;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: {text_color};
}}
"""
    
    return stylesheet
