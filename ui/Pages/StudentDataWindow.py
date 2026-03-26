from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt
import modules.DataSQL as data

def prettyPrint(msg: str):
    print("[STUDENT_FORM]:", msg)

fields = ["ID Number", "First Name", "Last Name", "Program Code", "Year Level", "Gender"]

class StudentFormDialog(QDialog):
    def __init__(self, parent=None, student_id=None):
        super().__init__(parent)
        
        self.student_id = student_id
        self.is_edit = student_id is not None
        self.entries = {}
 
        if self.is_edit:
            self.setWindowTitle(f"Edit Student")
        else:
            self.setWindowTitle("Add New Student")
        
        self.setGeometry(100, 100, 500, 400)

        self.setup_ui()
        
        if self.is_edit:
            self.load_student_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
   
        title_label = QLabel(f"{'Edit Student Information' if self.is_edit else 'Add New Student'}")
        title_label.setObjectName("FormTitle")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
  
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
    
        for i, field in enumerate(fields):
            if field == "Gender":
                continue
            
            label = QLabel(field + ":")
            entry = QLineEdit()
            entry.setMinimumWidth(300)
           
            if field == "ID Number" and self.is_edit:
                entry.setText(self.student_id)
                entry.setReadOnly(True)
            
            form_layout.addWidget(label, i, 0)
            form_layout.addWidget(entry, i, 1)
            self.entries[i] = entry

        gender_label = QLabel(fields[5] + ":")
        gender_options = ["Male", "Female", "Non-Binary"]
        gender_combo = QComboBox()
        gender_combo.addItems(gender_options)
        gender_combo.setMinimumWidth(300)
        
        form_layout.addWidget(gender_label, 5, 0)
        form_layout.addWidget(gender_combo, 5, 1)
        self.entries[5] = gender_combo
        
        layout.addLayout(form_layout)
  
        self.warn_label = QLabel("")
        self.warn_label.setObjectName("WarningLabel")
        self.warn_label.setStyleSheet("color: #B92905;")
        layout.addWidget(self.warn_label)
        
        layout.addStretch()
 
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Student")
        save_btn.setObjectName("SelectionButton")
        save_btn.clicked.connect(self.save_student)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SelectionButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_student_data(self):
        search = data.FindStudentData(self.student_id)
        if search:
            self.data_id = next(iter(search))
            data_content = search[self.data_id]
            data_format = data.GetFormat("Student")
         
            for i, field in enumerate(fields[1:5], start=1):
                value = data_content.get(data_format[i], "")
                self.entries[i].setText(str(value))
                prettyPrint(f"{i} {data_format[i]} {value}: {field}")

            gender_value = data_content.get(data_format[5], "")
            self.entries[5].setCurrentText(str(gender_value))
          
        else:
            prettyPrint(f"Student {self.student_id} not found!")
            self.warn_label.setText("Student not found.")
            self.warn_label.setStyleSheet("color: #B92905;")
    
    def save_student(self):
        self.warn_label.setText("")
        data_format = data.GetFormat("Student")
        to_pack = []
        
        for i, data_item in enumerate(data_format):
            if self.is_edit and i == 0:
                to_pack.append(self.student_id)
                continue
            else:
                inputted = self.entries[i].text().strip() if hasattr(self.entries[i], 'text') else self.entries[i].currentText()
            
            verified, msg = data.VerifyFormat(data_item, inputted, fields[i])
            
            if verified:
                to_pack.append(msg)
            else:
                self.warn_label.setText(msg)
                self.warn_label.setStyleSheet("color: #B92905;")
                return
        
        try:
            if self.is_edit:
                data.EditStudent(self.student_id, to_pack)
                self.warn_label.setText("Successfully saved.")
                self.warn_label.setStyleSheet("color: #2ECC71;")
                prettyPrint(f"Student {self.student_id} updated")
            else:
                data.AddStudent(to_pack)
                self.warn_label.setText("Student added successfully.")
                self.warn_label.setStyleSheet("color: #2ECC71;")
                prettyPrint(f"New student added")
         
            self.accept()
        except Exception as e:
            self.warn_label.setText(str(e))
            self.warn_label.setStyleSheet("color: #B92905;")
            prettyPrint(f"Error: {e}")
