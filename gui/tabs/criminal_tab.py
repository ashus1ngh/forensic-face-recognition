# gui/tabs/criminal_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QSpinBox, QTextEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt
from datetime import datetime

class CriminalDatabaseTab(QWidget):
    def __init__(self, db, user=None):
        super().__init__()
        self.db = db
        self.user = user or {'username': 'system', 'role': 'admin'}
        self.selected_criminal_id = None
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Title with user info
        title_layout = QHBoxLayout()
        title = QLabel("Criminal Database Management")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        user_label = QLabel(f"Logged in as: {self.user['username']} ({self.user['role']})")
        user_label.setStyleSheet("font-size: 11px; color: #666;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(user_label)
        main_layout.addLayout(title_layout)
        
        # Compact Form
        form_group = QGroupBox("Criminal Information")
        form_layout = QGridLayout()
        form_layout.setSpacing(5)
        
        # Row 1
        form_layout.addWidget(QLabel("Criminal ID:"), 0, 0)
        self.criminal_id_input = QLineEdit()
        self.criminal_id_input.setPlaceholderText("CR-2024-001")
        form_layout.addWidget(self.criminal_id_input, 0, 1)
        
        form_layout.addWidget(QLabel("Name:"), 0, 2)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        form_layout.addWidget(self.name_input, 0, 3)
        
        # Row 2
        form_layout.addWidget(QLabel("Age:"), 1, 0)
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 120)
        self.age_input.setMaximumWidth(80)
        form_layout.addWidget(self.age_input, 1, 1)
        
        form_layout.addWidget(QLabel("Height:"), 1, 2)
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("6'0\"")
        form_layout.addWidget(self.height_input, 1, 3)
        
        # Row 3
        form_layout.addWidget(QLabel("Case #:"), 2, 0)
        self.case_input = QLineEdit()
        form_layout.addWidget(self.case_input, 2, 1)
        
        form_layout.addWidget(QLabel("Jurisdiction:"), 2, 2)
        self.jurisdiction_input = QLineEdit()
        form_layout.addWidget(self.jurisdiction_input, 2, 3)
        
        # Row 4 - Text areas
        form_layout.addWidget(QLabel("Description:"), 3, 0, Qt.AlignTop)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Physical description")
        self.description_input.setMaximumHeight(50)
        form_layout.addWidget(self.description_input, 3, 1, 1, 3)
        
        # Row 5
        form_layout.addWidget(QLabel("Charges:"), 4, 0, Qt.AlignTop)
        self.charges_input = QTextEdit()
        self.charges_input.setPlaceholderText("Charges (comma separated)")
        self.charges_input.setMaximumHeight(50)
        form_layout.addWidget(self.charges_input, 4, 1, 1, 3)
        
        # Row 6
        form_layout.addWidget(QLabel("Notes:"), 5, 0, Qt.AlignTop)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Additional notes")
        self.notes_input.setMaximumHeight(50)
        form_layout.addWidget(self.notes_input, 5, 1, 1, 3)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add Criminal")
        self.add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        self.add_btn.clicked.connect(self.add_criminal)
        btn_layout.addWidget(self.add_btn)
        
        self.update_btn = QPushButton("✏️ Update Selected")
        self.update_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        self.update_btn.clicked.connect(self.update_criminal)
        self.update_btn.setEnabled(False)
        btn_layout.addWidget(self.update_btn)
        
        clear_btn = QPushButton("🔄 Clear Form")
        clear_btn.setStyleSheet("padding: 8px;")
        clear_btn.clicked.connect(self.clear_form)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # Table
        table_label = QLabel("Criminals in Database:")
        table_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Height', 
                                              'Charges', 'Case #', 'Jurisdiction', 
                                              'Status', 'Added By', 'Actions'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.setAlternatingRowColors(True)
        self.refresh_criminal_list()
        main_layout.addWidget(self.table)
        
        self.setLayout(main_layout)
    
    def add_criminal(self):
        if not self._validate_inputs():
            return
        
        try:
            criminal_data = self._get_form_data()
            criminal_data['added_by'] = self.user['username']
            criminal_data['added_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.db.add_criminal(**criminal_data)
            QMessageBox.information(self, "Success", f"Criminal '{criminal_data['name']}' added successfully!")
            self.clear_form()
            self.refresh_criminal_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add criminal: {str(e)}")
    
    def update_criminal(self):
        if not self.selected_criminal_id:
            return
        
        if not self._validate_inputs():
            return
        
        try:
            criminal_data = self._get_form_data()
            criminal_data['modified_by'] = self.user['username']
            criminal_data['modified_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.db.update_criminal(self.selected_criminal_id, **criminal_data)
            QMessageBox.information(self, "Success", "Criminal record updated successfully!")
            self.clear_form()
            self.refresh_criminal_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update criminal: {str(e)}")
    
    def _validate_inputs(self):
        criminal_id = self.criminal_id_input.text().strip()
        name = self.name_input.text().strip()
        charges = self.charges_input.toPlainText().strip()
        
        if not all([criminal_id, name, charges]):
            QMessageBox.warning(self, "Validation Error", 
                              "Please fill required fields:\n• Criminal ID\n• Name\n• Charges")
            return False
        return True
    
    def _get_form_data(self):
        return {
            'criminal_id': self.criminal_id_input.text().strip(),
            'name': self.name_input.text().strip(),
            'age': self.age_input.value() if self.age_input.value() > 0 else None,
            'height': self.height_input.text().strip() or None,
            'physical_description': self.description_input.toPlainText().strip() or None,
            'charges': self.charges_input.toPlainText().strip(),
            'status': 'active',
            'case_number': self.case_input.text().strip() or None,
            'jurisdiction': self.jurisdiction_input.text().strip() or None,
            'notes': self.notes_input.toPlainText().strip() or None
        }
    
    def clear_form(self):
        self.criminal_id_input.clear()
        self.name_input.clear()
        self.age_input.setValue(0)
        self.height_input.clear()
        self.description_input.clear()
        self.charges_input.clear()
        self.case_input.clear()
        self.jurisdiction_input.clear()
        self.notes_input.clear()
        self.selected_criminal_id = None
        self.update_btn.setEnabled(False)
        self.add_btn.setEnabled(True)
    
    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.selected_criminal_id = self.table.item(row, 0).data(Qt.UserRole)
            self.load_criminal_to_form(row)
            self.update_btn.setEnabled(True)
            self.add_btn.setEnabled(False)
    
    def load_criminal_to_form(self, row):
        self.criminal_id_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        age_text = self.table.item(row, 2).text()
        self.age_input.setValue(int(age_text) if age_text else 0)
        self.height_input.setText(self.table.item(row, 3).text())
        self.charges_input.setPlainText(self.table.item(row, 4).text())
        self.case_input.setText(self.table.item(row, 5).text())
        self.jurisdiction_input.setText(self.table.item(row, 6).text())
    
    def refresh_criminal_list(self):
        try:
            criminals = self.db.get_all_criminals()
            self.table.setRowCount(len(criminals))
            
            for row, criminal in enumerate(criminals):
                # Store actual DB ID for operations
                id_item = QTableWidgetItem(str(criminal[1]))  # Criminal ID
                id_item.setData(Qt.UserRole, criminal[0])  # Store database primary key
                self.table.setItem(row, 0, id_item)
                
                self.table.setItem(row, 1, QTableWidgetItem(criminal[2]))  # Name
                self.table.setItem(row, 2, QTableWidgetItem(str(criminal[3] or '')))  # Age
                self.table.setItem(row, 3, QTableWidgetItem(criminal[4] or ''))  # Height
                
                # Truncate charges for display
                charges = criminal[6][:40] + '...' if len(criminal[6]) > 40 else criminal[6]
                self.table.setItem(row, 4, QTableWidgetItem(charges))
                
                self.table.setItem(row, 5, QTableWidgetItem(criminal[9] or ''))  # Case #
                self.table.setItem(row, 6, QTableWidgetItem(criminal[10] or ''))  # Jurisdiction
                self.table.setItem(row, 7, QTableWidgetItem(criminal[8]))  # Status
                
                # Show who added it (if available)
                added_by = criminal[12] if len(criminal) > 12 else 'Unknown'
                self.table.setItem(row, 8, QTableWidgetItem(added_by))
                
                # Delete button
                delete_btn = QPushButton("🗑️ Delete")
                delete_btn.setStyleSheet("background-color: #f44336; color: white;")
                delete_btn.clicked.connect(lambda checked, cid=criminal[0]: self.delete_criminal(cid))
                self.table.setCellWidget(row, 9, delete_btn)
            
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh list: {str(e)}")
    
    def delete_criminal(self, criminal_id):
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            "Are you sure you want to delete this criminal record?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_criminal(criminal_id)
                QMessageBox.information(self, "Success", "Criminal record deleted successfully!")
                self.refresh_criminal_list()
                self.clear_form()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete criminal: {str(e)}")