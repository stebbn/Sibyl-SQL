import math

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QLineEdit, QLabel, QComboBox, QPushButton, QMenu, QTextEdit, 
                             QHeaderView, QAbstractItemView, QMessageBox, QButtonGroup, QStyledItemDelegate, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import modules.DataSQL as data
from modules.appFileHandler import resource_path
from modules.utils import center_window, play_sound
from ui.Pages.StudentDataWindow import StudentFormDialog

def prettyPrint(msg: str): 
    print("[DATA_REG]:", msg)

class RowColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        custom_bg = index.data(Qt.ItemDataRole.UserRole)
      
        if custom_bg:
            painter.fillRect(option.rect, QColor(custom_bg))
            
        super().paint(painter, option, index)

class DataPageFrame(QWidget):
    def __init__(self):
        super().__init__()
        
        self.data = []
        self.max_page_ye  = 10 # total page buttons to per ye
        self.current_page = 1
        self.page_offset  = None
        self.total_pages  = data.db._get_pages("students") or 1
        self.page_buttons = {}

        self.current_sort = 0
        self.reverse_sort = False
        self.right_clicked_row = None
        self.sort_columns_map  = {
            "ID No."        : "id_number", 
            "First Name"    : "first_name", 
            "Last Name"     : "last_name", 
            "Program"       : "program_code",
            "Year"          : "year_level", 
            "Gender"        : "gender"
        }

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

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Type to search...")
        self.search_entry.setMaximumHeight(32)
       
        self.search_field = QComboBox()
        self.search_field.addItems(["ID No.", "First Name", "Last Name", "Program", "Year", "Gender"])
        self.search_field.setMaximumWidth(150)
        self.search_field.setMaximumHeight(32)
       
        search_btn = QPushButton("Search")
        search_btn.setObjectName("SelectionButton")
        search_btn.setMaximumWidth(100)
        search_btn.setMaximumHeight(50)
        search_btn.clicked.connect(self.update_list)

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

        self.tree = QTableWidget()
        self.tree.setColumnCount(6)
        self.tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree.setHorizontalHeaderLabels(["ID No.", "First Name", "Last Name", "Program", "Year", "Gender"])

        self.delegate = RowColorDelegate(self.tree)
        self.tree.setItemDelegate(self.delegate)

        header = self.tree.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setDefaultSectionSize(100)

        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.verticalHeader().setVisible(False)

        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemSelectionChanged.connect(self.on_tree_select)
        self.tree.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
     
        page_buttons_container = QWidget()
        page_buttons_container.setMaximumHeight(40)
        main_page = QHBoxLayout(page_buttons_container)
      
        self.back_page  = self.make_page_button("<")
        self.next_page  = self.make_page_button(">")
        self.first_page = self.make_page_button("<<")
        self.last_page  = self.make_page_button(">>")

        self.back_page.clicked.connect(lambda: self.page_button_pressed("prev"))
        self.next_page.clicked.connect(lambda: self.page_button_pressed("next"))
        self.first_page.clicked.connect(lambda: self.page_button_pressed("first"))
        self.last_page.clicked.connect(lambda: self.page_button_pressed("last"))

        page_front = QHBoxLayout()
        page_front.setAlignment(Qt.AlignmentFlag.AlignLeft)

        page_front.addWidget(self.first_page)
        page_front.addWidget(self.back_page)

        self.page_button_layout = QHBoxLayout()
        self.page_button_layout.setSpacing(5)
   
        self.page_button_group = QButtonGroup(self)
        self.page_button_group.setExclusive(True)
        self.page_button_group.idClicked.connect(self.page_button_pressed)

        page_end = QHBoxLayout()
        page_end.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        page_end.addWidget(self.next_page)
        page_end.addWidget(self.last_page)

        self.info_frame = QGroupBox("Student Details")
        self.info_frame.setMaximumHeight(170)
        info_layout = QVBoxLayout(self.info_frame)
       
        self.display_box = QTextEdit()
        self.display_box.setReadOnly(True)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")

        # search section
        search_layout.addWidget(self.search_entry)
        search_layout.addWidget(QLabel("Field:"))
        search_layout.addWidget(self.search_field)

        # search section buttons
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addWidget(clear_btn)
        toolbar_layout.addWidget(add_btn)
        
        # add search
        main_layout.addWidget(toolbar_container)
           
        # tree
        main_layout.addWidget(self.tree)

        # page buttons
        main_page.addStretch()
        main_page.addLayout(page_front)
        main_page.addLayout(self.page_button_layout)
        main_page.addLayout(page_end)
        main_page.addStretch()

        self.load_page_buttons()
        main_layout.addWidget(page_buttons_container)
        
        # info box
        info_layout.addWidget(self.display_box)
        main_layout.addWidget(self.info_frame)
        main_layout.addWidget(self.status_label)
        
        self.show_info(self.search_entry.text())

    def clear_search(self):
        self.search_entry.clear()
        self.search_field.setCurrentIndex(0)
        self.update_list()
    
    def update_list(self):
        search_term = self.search_entry.text()
        self.current_page = 1
        self.show_info(search_term)
    
    def on_header_clicked(self, col):
        col_names = list(self.sort_columns_map.keys())
        self.sort_column_name = col_names[col] if col < len(col_names) else col_names[0]

        if self.current_sort == col:
            self.reverse_sort = not self.reverse_sort
        else:
            self.current_sort = col
            self.reverse_sort = False
        
        self.show_info(self.search_entry.text())
    
    def on_tree_select(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        
        row = self.tree.row(selected_items[0])
        student_id = self.tree.item(row, 0).text()
        
        for students in self.data:
            if str(students["id_number"]) != student_id: 
                continue

            program_code = students["program_code"]
            college_details = data.GetProgramDetails(program_code)

            if college_details:
                program_name = college_details["program_name"]
                college_name = college_details["college_name"]
            else:
                program_name = "Unknown Program"
                college_name = "Unknown College"
            
            self.display_box.clear()
            
            html_text = f"""
                        <b>ID NUMBER:</b> {student_id}<br>
                        <b>FULL NAME:</b> {students["first_name"]} {students["last_name"]}<br>
                        <b>ACADEMICS:</b> {program_name} (Year {students["year_level"]})<br>
                        <b>COLLEGE:</b> {college_name} <br>
                        <b>GENDER:</b> {students["gender"]}
                        """
            
            self.display_box.setHtml(html_text)
            break
    
    def show_info(self, search_query=""):

        search_query = search_query.lower()
        field_filter = self.search_field.currentText()
        filtered_field = self.sort_columns_map.get(field_filter) or None

        if not filtered_field: prettyPrint(f"error on field filter {filtered_field}")

        self.data, self.total_pages = data.db.query_students(
                                        search          = search_query, 
                                        search_field    = filtered_field, 
                                        page            = self.current_page, 
                                        sort            = self.sort_columns_map.get(self.sort_column_name),
                                        asc             = not self.reverse_sort
                                    )
        self.tree.setRowCount(0)
        self.load_page_buttons()
        
        for students in self.data:
            student_id = str(students["id_number"])
            first_name = str(students["first_name"])
            last_name  = str(students["last_name"])
            program    = str(students["program_code"])
            year       = str(students["year_level"])
            gender     = str(students["gender"])

            field_map = {
                "ID No."        : student_id,
                "First Name"    : first_name,
                "Last Name"     : last_name,
                "Program"       : program,
                "Year"          : year,
                "Gender"        : gender,
            }

            target_text = str(field_map.get(field_filter, "")).lower()
            
            if not search_query or search_query in target_text:
                row = self.tree.rowCount()
                self.tree.insertRow(row)
                
                id_item         = QTableWidgetItem(student_id)
                first_name_item = QTableWidgetItem(first_name)
                last_name_item  = QTableWidgetItem(last_name)
                program_item    = QTableWidgetItem(program)
                year_item       = QTableWidgetItem(year)
                gender_item     = QTableWidgetItem(gender)
                
                prog_stat = data.get_college_by_program(program)

                if prog_stat == "invalid program code":
                    prettyPrint(f"warning: {student_id}")
                    for item in [id_item, first_name_item, last_name_item, program_item, year_item, gender_item]:
                        item.setData(Qt.ItemDataRole.UserRole, "#DDD239")
                elif prog_stat == "College Not Found":
                    prettyPrint(f"error: {student_id}")
                    for item in [id_item, first_name_item, last_name_item, program_item, year_item, gender_item]:
                        item.setData(Qt.ItemDataRole.UserRole, "#DD3939")
                    
                self.tree.setItem(row, 0, id_item)
                self.tree.setItem(row, 1, first_name_item)
                self.tree.setItem(row, 2, last_name_item)
                self.tree.setItem(row, 3, program_item)
                self.tree.setItem(row, 4, year_item)
                self.tree.setItem(row, 5, gender_item)
        
        self.status_label.setText(f"Total Students: {data.db._get_table_val("students", "Total")} | Current Pages: {self.total_pages}")

        prettyPrint(f"Added {self.tree.rowCount()} rows to table")
        
    def show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if item:
            self.right_clicked_row = self.tree.row(item)
            menu = QMenu(self)
            menu.addAction("Edit Student", self.edit_student)
            menu.addAction("Delete Student", self.delete_student)
            menu.exec(self.tree.mapToGlobal(position))
    
    def open_add_student_window(self):
        dialog = StudentFormDialog(self)
        center_window(dialog, dialog.width(), dialog.height())

        if dialog.exec() == StudentFormDialog.DialogCode.Accepted:
            self.show_info(self.search_entry.text())
    
    def open_edit_student_window(self, student_id: str):
        dialog = StudentFormDialog(self, student_id=student_id)
        center_window(dialog, dialog.width(), dialog.height())

        if dialog.exec() == StudentFormDialog.DialogCode.Accepted:
            self.show_info(self.search_entry.text())
    
    def edit_student(self):
        row = self.right_clicked_row if self.right_clicked_row is not None else self.tree.currentRow()
        if row is not None and row >= 0:
            student_id = self.tree.item(row, 0).text()
            self.open_edit_student_window(student_id)
            self.right_clicked_row = None
    
    def delete_student(self):
        row = self.right_clicked_row if self.right_clicked_row is not None else self.tree.currentRow()
        if row is not None and row >= 0:
            student_id = self.tree.item(row, 0).text()
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       f"Delete student {student_id}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                if data.DeleteStudent(student_id):
                    self.show_info(self.search_entry.text())
            self.right_clicked_row = None
        else:
            prettyPrint("did not select anything")
    
    
    def switch_page(self, val):
        val_edit = max(1, min(val, self.total_pages)) 
        if self.current_page == val_edit : prettyPrint("same page"); return

        self.current_page = val_edit
        self.show_info(self.search_entry.text())  
        self.load_page_buttons()
    
    def page_button_pressed(self, val):
        assert(isinstance(val, str) or isinstance(val, int), "???")
        if type(val) is str: 
            if   val == "first": val = 1
            elif val == "prev" : val = self.current_page - 1
            elif val == "next" : val = self.current_page + 1
            elif val == "last" : val = self.total_pages       # this sucks
            else: prettyPrint(f"unknown str val: {val}"); return
        
        self.switch_page(val)
        play_sound(resource_path("ui/Assets/Sounds/button_click.wav"))

    def make_page_button(self, n):
        page_b = QPushButton(str(n))
        page_b.setObjectName("SelectionButton")
        page_b.setFixedHeight(45)
        page_b.setFixedWidth(40)
        page_b.setStyleSheet("text-align: center;")
        return page_b

    def load_page_buttons(self):
        if not getattr(self, "total_pages", None):
            self.total_pages = 1

        chunk = ((self.current_page - 1) // self.max_page_ye) * self.max_page_ye + 1

        if (getattr(self, "page_offset", None) != chunk) or (getattr(self, "last_total_pages", None) != self.total_pages):
            
            for button in self.page_button_group.buttons():
                self.page_button_group.removeButton(button)
                self.page_button_layout.removeWidget(button)
                button.deleteLater()
            
            self.page_offset = chunk   
            self.last_total_pages = self.total_pages
            
            chunk_end = min(self.total_pages, chunk + self.max_page_ye - 1)
       
            for page_count in range(chunk, chunk_end + 1):
                btn = self.make_page_button(page_count)
                btn.setCheckable(True)

                self.page_button_layout.addWidget(btn)
                self.page_button_group.addButton(btn, id=page_count)

        active_btn = self.page_button_group.button(self.current_page)
        if active_btn:
            active_btn.setChecked(True)
    
    
    def keyPressEvent(self, event):
        def handle_enter():
            if self.tree.currentRow() >= 0:
                student_id = self.tree.item(self.tree.currentRow(), 0).text()
                self.open_edit_student_window(student_id)
            else:
                self.update_list()

        keybinds = {
            Qt.Key.Key_Delete: self.delete_student,
            Qt.Key.Key_Return: handle_enter,
            Qt.Key.Key_Enter: handle_enter,
            (Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier): self.open_add_student_window,
            (Qt.Key.Key_F, Qt.KeyboardModifier.ControlModifier): self.search_entry.setFocus
        }

        combo = (event.key(), event.modifiers())
      
        if combo in keybinds:
            keybinds[combo]()
        elif event.key() in keybinds:
            keybinds[event.key()]()
        else:
            super().keyPressEvent(event)