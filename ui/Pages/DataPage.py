from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QLabel, QComboBox, QPushButton, QMenu, QTextEdit, 
                             QHeaderView, QAbstractItemView, QMessageBox, QFrame, QScrollArea, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import modules.Data as data

from modules.utils import center_window
from ui.Pages.StudentDataWindow import StudentFormDialog

def prettyPrint(msg: str): 
    print("[DATA_REG]:", msg)

class DataPageFrame(QWidget):
    def __init__(self):
        super().__init__()
        
        self.current_sort = 0
        self.reverse_sort = False
        self.right_clicked_row = None
        self.sort_column_name = "ID No." 
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
       
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
        self.search_entry.setPlaceholderText("Type to search...")
        self.search_entry.textChanged.connect(self.update_list)
        self.search_entry.setMaximumHeight(32)
       
        self.search_field = QComboBox()
        self.search_field.addItems(["Match", "ID No.", "First Name", "Last Name", "Program", "Year", "Gender"])
        self.search_field.currentTextChanged.connect(self.update_list)
        self.search_field.setMaximumWidth(150)
        self.search_field.setMaximumHeight(32)
       
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("SelectionButton")
        clear_btn.setMaximumWidth(100)
        clear_btn.setMaximumHeight(50)
        clear_btn.clicked.connect(self.clear_search)

        add_btn = QPushButton("Add")
        add_btn.setObjectName("SelectionButton")
        add_btn.setMaximumWidth(70)
        add_btn.setMaximumHeight(50)
        add_btn.clicked.connect(self.open_add_student_window)

        toolbar_layout.addLayout(search_layout, 1)

        search_layout.addWidget(self.search_entry)
        search_layout.addWidget(QLabel("Field:"))
        search_layout.addWidget(self.search_field)

        toolbar_layout.addWidget(clear_btn)
        toolbar_layout.addWidget(add_btn)
        
        main_layout.addWidget(toolbar_container)

        self.tree = QTableWidget()
        self.tree.setColumnCount(6)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.tree.setHorizontalHeaderLabels(["ID No.", "First Name", "Last Name", "Program", "Year", "Gender"])

        header = self.tree.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemSelectionChanged.connect(self.on_tree_select)
        self.tree.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        main_layout.addWidget(self.tree)

        self.info_frame = QGroupBox("Student Details")
        self.info_frame.setMaximumHeight(170)
        info_layout = QVBoxLayout(self.info_frame)
       
        self.display_box = QTextEdit()
        self.display_box.setReadOnly(True)
        info_layout.addWidget(self.display_box)
        
        main_layout.addWidget(self.info_frame)

        self.status_label = QLabel("Loading...")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        main_layout.addWidget(self.status_label)
        
        self.show_info()
    
    def clear_search(self):
        self.search_entry.clear()
        self.search_field.setCurrentIndex(0)
        self.update_list()
    
    def update_list(self):
        search_term = self.search_entry.text()
        self.show_info(search_term)
    
    def on_header_clicked(self, col):
        col_names = ["ID No.", "First Name", "Last Name", "Program", "Year", "Gender"]
        self.sort_column_name = col_names[col] if col < len(col_names) else col_names[0]

        if self.current_sort == col:
            self.reverse_sort = not self.reverse_sort
        else:
            self.current_sort = col
            self.reverse_sort = False
        
        self.show_info(self.search_entry.text())
        prettyPrint(f"Sorted by {self.sort_column_name} ({'descending' if self.reverse_sort else 'ascending'})")
    
    
    
    def on_tree_select(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        row = self.tree.row(selected_items[0])
        student_id = self.tree.item(row, 0).text()
        
        if student_id in data.student_data:
            value = data.student_data[student_id]
            college = data.get_college_by_program(value.get('program_code', ''))

            program_code = value.get('program_code', '')
            program_info = data.program_data.get(program_code, {})
            program_name = program_info.get('name', 'Unknown Program')
            
            self.display_box.clear()
            
            html_text = f"""<b>ID NUMBER:</b> {student_id}<br>
                        <b>FULL NAME:</b> {value.get('last_name', '')}, {value.get('first_name', '')}<br>
                        <b>ACADEMICS:</b> {program_name} (Year {value.get('year', '')})<br>
                        <b>COLLEGE:</b> {college if college not in ['invalid program code', 'College Not Found'] else '-'}<br>
                        <b>GENDER:</b> {value.get('gender', '')}"""
            
            self.display_box.setHtml(html_text)
    
    def update_list(self):
        search_term = self.search_var
        self.show_info(search_term)
    
    def show_info(self, search_query=""):
        self.tree.setRowCount(0)
        
        student_records = data.student_data
        prettyPrint(f"show_info called with {len(student_records)} records")
        search_query = search_query.lower()
        field_filter = self.search_field.currentText()
        
        for student_id, value in student_records.items():
            field_map = {
                "ID No.": student_id,
                "First Name": value.get('first_name', ''),
                "Last Name": value.get('last_name', ''),
                "Program": value.get('program_code', ''),
                "Year": str(value.get('year', '')),
                "Gender": value.get('gender', '')
            }
            
            if field_filter == "Match":
                target_text = f"{student_id} {' '.join(str(v) for v in value.values())}".lower()
            else:
                target_text = str(field_map.get(field_filter, "")).lower()
            
            if not search_query or search_query in target_text:
                row = self.tree.rowCount()
                self.tree.insertRow(row)
                
                # Create items
                id_item = QTableWidgetItem(student_id)
                first_name_item = QTableWidgetItem(value.get("first_name", ""))
                last_name_item = QTableWidgetItem(value.get("last_name", ""))
                program_item = QTableWidgetItem(value.get("program_code", ""))
                year_item = QTableWidgetItem(str(value.get("year", "")))
                gender_item = QTableWidgetItem(value.get("gender", ""))
                
                if row == 0:  # Debug first row
                    prettyPrint(f"First row values: ID={student_id}, Name={value.get('first_name', '')} {value.get('last_name', '')}")
                
                # Check program validity and set colors
                prog_stat = data.get_college_by_program(value.get("program_code", ""))
                if prog_stat == "invalid program code":
                    for item in [id_item, first_name_item, last_name_item, program_item, year_item, gender_item]:
                        item.setForeground(QColor("#FF6B6B"))
                elif prog_stat == "College Not Found":
                    for item in [id_item, first_name_item, last_name_item, program_item, year_item, gender_item]:
                        item.setForeground(QColor("#FFDC6B"))
                
                self.tree.setItem(row, 0, id_item)
                self.tree.setItem(row, 1, first_name_item)
                self.tree.setItem(row, 2, last_name_item)
                self.tree.setItem(row, 3, program_item)
                self.tree.setItem(row, 4, year_item)
                self.tree.setItem(row, 5, gender_item)
        
        prettyPrint(f"Added {self.tree.rowCount()} rows to table")
        self.sort_column(self.current_sort, self.reverse_sort)
        
        # Update status bar
        total = len(data.student_data)
        shown = self.tree.rowCount()
        if search_query:
            self.status_label.setText(f"📊 Showing {shown} of {total} students • Sorted by {self.sort_column_name}")
        else:
            self.status_label.setText(f"📊 Total {total} students • Sorted by {self.sort_column_name}")
    
    def show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if item:
            self.right_clicked_row = self.tree.row(item)
            menu = QMenu(self)
            menu.addAction("Edit Student", self.edit_student)
            menu.addAction("Delete Student", self.delete_student)
            menu.exec(self.tree.mapToGlobal(position))
    
    def sort_column(self, col, reverse):
        # Get all rows
        rows = []
        for row in range(self.tree.rowCount()):
            row_data = []
            for col_idx in range(self.tree.columnCount()):
                item = self.tree.item(row, col_idx)
                row_data.append((item.text() if item else "", row))
            rows.append(row_data)
        
        # Sort based on column
        try:
            rows.sort(key=lambda x: int(x[col][0].split('-')[0]) if '-' in x[col][0] else int(x[col][0]), 
                     reverse=reverse)
        except (ValueError, IndexError):
            rows.sort(key=lambda x: x[col][0].lower(), reverse=reverse)
        
        # Store sorted data and restore to table
        for new_row, row_data in enumerate(rows):
            for col_idx, (text, old_row) in enumerate(row_data):
                item = self.tree.item(old_row, col_idx)
                if item:
                    # Create a new item with existing data
                    new_item = QTableWidgetItem(text)
                    # Preserve any formatting (colors, etc.)
                    new_item.setForeground(item.foreground())
                    self.tree.setItem(new_row, col_idx, new_item)
        
        self.current_sort = col
        self.reverse_sort = reverse
    
    def open_add_student_window(self):
        dialog = StudentFormDialog(self)
        center_window(dialog, dialog.width(), dialog.height())

        if dialog.exec() == StudentFormDialog.DialogCode.Accepted:
            self.show_info()
    
    def open_edit_student_window(self, student_id: str):
        prettyPrint(f"Opening edit dialog for student: {student_id}")

        dialog = StudentFormDialog(self, student_id=student_id)
        center_window(dialog, dialog.width(), dialog.height())

        prettyPrint(f"Dialog created and centered, executing...")
        result = dialog.exec()
        prettyPrint(f"Dialog result: {result}")
        if result == StudentFormDialog.DialogCode.Accepted:
            self.show_info()
    
    def edit_student(self):
        row = self.right_clicked_row
        if row is not None and row >= 0:
            student_id = self.tree.item(row, 0).text()
            self.open_edit_student_window(student_id)
    
    def delete_student(self):
        row = self.right_clicked_row
        if row is not None and row >= 0:
            student_id = self.tree.item(row, 0).text()
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       f"Delete student {student_id}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if data.DeleteStudent(student_id):
                    self.show_info()
        else:
            prettyPrint("did not select anything")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_student()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.tree.currentRow() >= 0:
                student_id = self.tree.item(self.tree.currentRow(), 0).text()
                self.open_edit_student_window(student_id)
        elif event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.open_add_student_window()
        elif event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.search_entry.setFocus()
        else:
            super().keyPressEvent(event)