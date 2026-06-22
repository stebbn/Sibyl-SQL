from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel, QDialog, 
                             QComboBox, QMessageBox, QMenu, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import modules.DataSQL as data

from modules.appFileHandler import resource_path
from modules.utils import play_sound

def prettyPrint(msg: str): 
    print("[COLLEGE_PAGE]:", msg)

def throw_error(self, text, message, choices):
    return QMessageBox.question(self, text, message, choices)

class CollegeFinderFrame(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.notebook = QTabWidget()
        
        self.tab_colleges = CollegeTab()
        self.tab_programs = ProgramTab()
        
        self.notebook.addTab(self.tab_colleges, "Colleges")
        self.notebook.addTab(self.tab_programs, "Programs")
        
        layout.addWidget(self.notebook)

        self.notebook.tabBarClicked.connect(self.on_tab_click)

    def on_tab_click(self):
        self.tab_programs.refresh()
        self.tab_colleges.refresh()

class CollegeTab(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 3, 0, 0)

        self.data = data.db.query_college()
        
        toolbar_container = QWidget()

        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 2, 0, 0)
        toolbar_layout.setSpacing(10)

        search_layout = QHBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setSpacing(5)
        search_layout.addWidget(QLabel("Search:"))

        self.search_entry = QLineEdit()
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("SelectionButton")
        search_btn.clicked.connect(self.refresh)

        clear_buton = QPushButton("Clear")
        clear_buton.setObjectName("SelectionButton")
        clear_buton.clicked.connect(self.on_clear)

        add_btn = QPushButton("+")
        add_btn.setObjectName("SelectionButton")
        add_btn.clicked.connect(lambda: self.open_editor())

        toolbar_layout.addLayout(search_layout, 1)
        search_layout.addWidget(self.search_entry)

        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addWidget(clear_buton)
        toolbar_layout.addWidget(add_btn)
        
        layout.addWidget(toolbar_container)

        self.tree = QTableWidget()
        self.tree.setColumnCount(2)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.tree.setHorizontalHeaderLabels(["Code", "College Name"])
        self.tree.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_menu)
        self.tree.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        layout.addWidget(self.tree)
        
        self.current_sort = 0
        self.reverse_sort = False
        
        self.refresh()
    
    def on_clear(self):
        self.search_entry.clear()
        self.refresh()
    
    def on_cell_double_clicked(self, row, col):
        if row >= 0:
            self.edit_selected()
    
    def sort_column(self, col, reverse):
        self.tree.sortItems(col, Qt.SortOrder.DescendingOrder if reverse else Qt.SortOrder.AscendingOrder)
        self.current_sort = col
        self.reverse_sort = reverse
    
    def update_data(self):
        self.data = data.db.query_college()

    def refresh(self):
        self.tree.setRowCount(0)
        self.update_data()
        
        search_term = self.search_entry.text().strip().lower()
        
        for college in self.data:
            code = str(college["college_code"])  
            name = str(college["college_name"])
  
            if search_term:
                if search_term not in code.lower() and search_term not in name.lower():
                    continue
            
            row = self.tree.rowCount()
            self.tree.insertRow(row)
            
            item_code = QTableWidgetItem(code)
            item_name = QTableWidgetItem(name)
            
            self.tree.setItem(row, 0, item_code)
            self.tree.setItem(row, 1, item_name)
    
    def show_menu(self, position):
        menu = QMenu(self)
        menu.addAction("Edit", self.edit_selected)
        menu.addAction("Delete", self.delete_selected)
        menu.exec(self.tree.mapToGlobal(position))
    
    def edit_selected(self):
        row = self.tree.currentRow()
        if row >= 0:
            code = self.tree.item(row, 0).text()
            name = self.tree.item(row, 1).text()
            self.open_editor({"code": code, "name": name})
    
    def delete_selected(self):
        row = self.tree.currentRow()
        if row >= 0:
            code = self.tree.item(row, 0).text()
            
            safe_del = data.checkCollegeDelete(code)
            college_format = f"{code} | {data.get_college_name(code)}"

            if row >= 0:

                msg =  f"Delete College ({college_format})?" 
                choices = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No

                if (safe_del != True) and type(safe_del) == list:
                    msg = f"Deleting College ({college_format}) will result into unassigning {safe_del[0]} programs with {safe_del[1]} students." 
                elif (safe_del != True) and type(safe_del) != list:
                    msg = f"{safe_del}"
                    choices = QMessageBox.StandardButton.Ok

                play_sound(resource_path("ui/Assets/Sounds/error.wav"), volume = 0.2)
                reply = throw_error(self, "Confirm Delete", msg, choices)

            if reply == QMessageBox.StandardButton.Yes:
                data.DeleteCollege(code)
                self.refresh()
                
    
    def open_editor(self, info=None):
        editor = EditorWindow(self, "college", info)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

class ProgramTab(QWidget):
    def __init__(self):
        super().__init__()

        self.get_data()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 3, 0, 0)
        
        toolbar_container = QWidget()

        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 2, 0, 0)
        toolbar_layout.setSpacing(10)

        search_layout = QHBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setSpacing(5)
        search_layout.addWidget(QLabel("Search:"))
    
        self.search_entry = QLineEdit()
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("SelectionButton")
        search_btn.clicked.connect(self.refresh)
        
        clear_buton = QPushButton("Clear")
        clear_buton.setObjectName("SelectionButton")
        clear_buton.clicked.connect(self.on_clear)

        add_btn = QPushButton("+")
        add_btn.setObjectName("SelectionButton")
        add_btn.clicked.connect(lambda: self.open_editor())

        toolbar_layout.addLayout(search_layout,1)
        search_layout.addWidget(self.search_entry)

        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addWidget(clear_buton)
        toolbar_layout.addWidget(add_btn)
        
        layout.addWidget(toolbar_container)
        
        self.tree = QTableWidget()
        self.tree.setColumnCount(3)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.tree.setHorizontalHeaderLabels(["Code", "Program Name", "College"])
        self.tree.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.tree.customContextMenuRequested.connect(self.show_menu)
        self.tree.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        layout.addWidget(self.tree)
        
        self.current_sort = 0
        self.reverse_sort = False
        
        self.refresh()
    
    def on_clear(self):
        self.search_entry.clear()
        self.refresh()
    
    def on_cell_double_clicked(self, row, col):
        if row >= 0:
            self.edit_selected()
    
    def get_data(self):
        self.data = data.db.query_programs()

    def refresh(self):
        self.tree.setRowCount(0)
        self.get_data()

        search_term = self.search_entry.text().strip().lower()
        
        for program in self.data:
            code = str(program["program_code"])
            name = str(program["program_name"])
            col_code = str(program["college_code"])
        
            if search_term:
                if (search_term not in code.lower() and 
                    search_term not in name.lower() and 
                    search_term not in col_code.lower()):
                    continue
            
            row = self.tree.rowCount()
            self.tree.insertRow(row)
            
            item_code = QTableWidgetItem(code)
            item_name = QTableWidgetItem(name)
            item_college = QTableWidgetItem(col_code)
            
            self.tree.setItem(row, 0, item_code)
            self.tree.setItem(row, 1, item_name)
            self.tree.setItem(row, 2, item_college)
    
    def show_menu(self, position):
        menu = QMenu(self)
        menu.addAction("Edit", self.edit_selected)
        menu.addAction("Delete", self.delete_selected)
        menu.exec(self.tree.mapToGlobal(position))
    
    def edit_selected(self):
        row = self.tree.currentRow()
        if row >= 0:
            code = self.tree.item(row, 0).text()
            name = self.tree.item(row, 1).text()
            college_code = self.tree.item(row, 2).text()
            self.open_editor({"code": code, "name": name, "college_code": college_code})
    
    def delete_selected(self):
        row = self.tree.currentRow()
        if row >= 0:
            code = self.tree.item(row, 0).text()
            affected_students = data.get_students_in_program((str(code),))

            msg = f"Delete program {code}?"

            if affected_students > 0:
                msg = f"Deleting program: {code} is going to unassign {affected_students} students. Delete?"

            play_sound(resource_path("ui/Assets/Sounds/error.wav"), volume = 0.2)
            reply = throw_error(self, "Confirm Delete", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                data.DeleteProgram(code)
                self.refresh()
    
    def open_editor(self, info=None):
        editor = EditorWindow(self, "program", info)
        if editor.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

class EditorWindow(QDialog):
    def __init__(self, parent, mode, info=None):
        super().__init__(parent)
        
        self.mode = mode
        self.info = info
        self.is_edit = info is not None
        self.parent = parent
        
        self.setWindowTitle(f"{'Edit' if self.is_edit else 'Add'} {mode.title()}")
        self.setModal(True)
        self.setup_ui()
        self.setMinimumWidth(400)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        if self.mode == "college":
            layout.addWidget(QLabel(f"{self.mode.title()} Code:"))
            self.code_input = QLineEdit()
            self.code_input.setReadOnly(self.is_edit)
            if self.is_edit:
                self.code_input.setText(self.info["code"])
            layout.addWidget(self.code_input)
            
            layout.addWidget(QLabel("College Name:"))
            self.name_input = QLineEdit()
            if self.is_edit:
                self.name_input.setText(self.info["name"])
            layout.addWidget(self.name_input)
        
        elif self.mode == "program":
            layout.addWidget(QLabel(f"{self.mode.title()} Code:"))
            self.code_input = QLineEdit()
            self.code_input.setReadOnly(self.is_edit)
            if self.is_edit:
                self.code_input.setText(self.info["code"])
            layout.addWidget(self.code_input)
            
            layout.addWidget(QLabel("Program Name:"))
            self.name_input = QLineEdit()
            if self.is_edit:
                self.name_input.setText(self.info["name"])
            layout.addWidget(self.name_input)
            
            layout.addWidget(QLabel("College Code:"))
            self.college_input = QComboBox()
            self.college_input.addItems(data.get_colleges())

            if self.is_edit:
                index = self.college_input.findText(self.info.get("college_code", ""))
                if index >= 0:
                    self.college_input.setCurrentIndex(index)
            layout.addWidget(self.college_input)
        
        layout.addStretch()
  
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Data")
        save_btn.setObjectName("SelectionButton")

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SelectionButton")

        save_btn.clicked.connect(self.save)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def save(self):
        try:
            code = self.code_input.text().strip()
            name = self.name_input.text().strip()
            
            prettyPrint(f"attempt to {'Edit' if self.is_edit else 'Add'}: {self.mode}")
            
            if self.mode == "college":
                if self.is_edit:
                    result, error = data.EditCollege(code, name)
                    if not result: throw_error(self, "Save Error", error, QMessageBox.StandardButton.Ok)
                else:
                    result, error = data.AddCollege([code, name])
                    if not result: throw_error(self, "Save Error", error, QMessageBox.StandardButton.Ok)
            
            elif self.mode == "program":
                college = self.college_input.currentText()
                if self.is_edit:
                    result, error = data.EditProgram(code, [code, name, college])
                    if not result: throw_error(self, "Save Error", error, QMessageBox.StandardButton.Ok)
                else:
                    result, error = data.AddProgram([code, name, college])
                    if not result: throw_error(self, "Save Error", error, QMessageBox.StandardButton.Ok)
            
            self.parent.refresh()
            self.accept()
        except Exception as e:
            prettyPrint(f"Error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")