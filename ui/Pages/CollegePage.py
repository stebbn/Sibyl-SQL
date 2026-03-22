from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLineEdit, QLabel, QDialog, 
                             QComboBox, QMessageBox, QMenu, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import modules.DataSQL as data

def prettyPrint(msg: str): 
    print("[COLLEGE_PAGE]:", msg)

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

        self.search_var = ""
        self.search_entry = QLineEdit()
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("SelectionButton")
        search_btn.clicked.connect(self.refresh)

        add_btn = QPushButton("+")
        add_btn.setObjectName("SelectionButton")
        add_btn.clicked.connect(lambda: self.open_editor())

        toolbar_layout.addLayout(search_layout, 1)

        search_layout.addWidget(self.search_entry)

        toolbar_layout.addWidget(search_btn)
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
    
    def on_search_changed(self, text):
        self.search_var = text
    
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
        
        for college in self.data:
            row = self.tree.rowCount()
            self.tree.insertRow(row)

            code = str(college["college_code"])  
            name = str(college["college_name"])
            
            item_code = QTableWidgetItem(code)
            item_name = QTableWidgetItem(name)
            
            self.tree.setItem(row, 0, item_code)
            self.tree.setItem(row, 1, item_name)
    
    def show_menu(self, position):
        menu = QMenu(self)
        menu.addAction("Edit", self.edit_selected)
        menu.addAction("Delete", self.delete_selected)
        menu.addAction("Add New", lambda: self.open_editor())
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
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       f"Delete college {code}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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

        self.data = data.db.query_programs()

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
        
        self.search_var = ""
        self.search_entry = QLineEdit()
        self.search_entry.textChanged.connect(self.on_search_changed)
        
        search_btn = QPushButton("Search")
        search_btn.setObjectName("SelectionButton")
        search_btn.clicked.connect(self.refresh)
        
        add_btn = QPushButton("+")
        add_btn.setObjectName("SelectionButton")
        add_btn.clicked.connect(lambda: self.open_editor())

        toolbar_layout.addLayout(search_layout,1)
        search_layout.addWidget(self.search_entry)

        toolbar_layout.addWidget(search_btn)
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
    
    def on_search_changed(self, text):
        self.search_var = text
    
    def on_cell_double_clicked(self, row, col):
        if row >= 0:
            self.edit_selected()
    
    def refresh(self):
        self.tree.setRowCount(0)
        
        for program in self.data:
            row = self.tree.rowCount()
            self.tree.insertRow(row)

            code = str(program["program_code"])
            name = str(program["program_name"])
            col_code = str(program["college_code"])
            
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
        menu.addAction("Add New", lambda: self.open_editor())
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
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       f"Delete program {code}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
            self.college_input.addItems(data.college_data.keys())
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
                    data.EditCollege(code, name)
                else:
                    data.AddCollege([code, name])
            
            elif self.mode == "program":
                college = self.college_input.currentText()
                if self.is_edit:
                    data.EditProgram(code, [code, name, college])
                else:
                    data.AddProgram([code, name, college])
            
            self.parent.refresh()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
            prettyPrint(f"Error: {e}")