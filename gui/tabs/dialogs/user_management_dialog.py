"""
User Management Dialog - Manage system users (Admin only)
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                              QLineEdit, QComboBox, QMessageBox, QGroupBox,
                              QInputDialog, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from datetime import datetime


class UserManagementDialog(QDialog):
    """Dialog for managing system users"""
    
    def __init__(self, auth_manager, current_user, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.current_user = current_user
        
        self.setWindowTitle("User Management")
        self.setMinimumSize(900, 600)
        
        self.init_ui()
        self.load_users()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("👥 User Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # User table
        table_group = QGroupBox("System Users")
        table_layout = QVBoxLayout()
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(7)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Username", "Full Name", "Email", "Role", "Status", "Last Login"
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.user_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.user_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.user_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        table_layout.addWidget(self.user_table)
        table_group.setLayout(table_layout)
        
        # Action buttons
        button_group = QGroupBox("Actions")
        button_layout = QHBoxLayout()
        
        self.btn_add_user = QPushButton("➕ Add User")
        self.btn_edit_user = QPushButton("✏️ Edit User")
        self.btn_delete_user = QPushButton("🗑️ Delete User")
        self.btn_reset_password = QPushButton("🔑 Reset Password")
        self.btn_toggle_status = QPushButton("🔄 Toggle Status")
        
        self.btn_add_user.clicked.connect(self.add_user)
        self.btn_edit_user.clicked.connect(self.edit_user)
        self.btn_delete_user.clicked.connect(self.delete_user)
        self.btn_reset_password.clicked.connect(self.reset_password)
        self.btn_toggle_status.clicked.connect(self.toggle_status)
        
        # Initially disable edit/delete buttons
        self.btn_edit_user.setEnabled(False)
        self.btn_delete_user.setEnabled(False)
        self.btn_reset_password.setEnabled(False)
        self.btn_toggle_status.setEnabled(False)
        
        button_layout.addWidget(self.btn_add_user)
        button_layout.addWidget(self.btn_edit_user)
        button_layout.addWidget(self.btn_delete_user)
        button_layout.addWidget(self.btn_reset_password)
        button_layout.addWidget(self.btn_toggle_status)
        button_group.setLayout(button_layout)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.lbl_total_users = QLabel("Total Users: 0")
        self.lbl_active_users = QLabel("Active Users: 0")
        self.lbl_admin_users = QLabel("Administrators: 0")
        
        stats_layout.addWidget(self.lbl_total_users)
        stats_layout.addWidget(self.lbl_active_users)
        stats_layout.addWidget(self.lbl_admin_users)
        stats_group.setLayout(stats_layout)
        stats_group.setMaximumHeight(120)
        
        # Close button
        close_layout = QHBoxLayout()
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        close_layout.addStretch()
        close_layout.addWidget(self.btn_close)
        
        # Add all to main layout
        layout.addWidget(table_group, 1)
        layout.addWidget(button_group)
        layout.addWidget(stats_group)
        layout.addLayout(close_layout)
        
        self.setLayout(layout)
        
    def load_users(self):
        """Load all users into table"""
        users = self.auth_manager.get_all_users()
        
        self.user_table.setRowCount(0)
        
        for user in users:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
            self.user_table.setItem(row, 1, QTableWidgetItem(user['username']))
            self.user_table.setItem(row, 2, QTableWidgetItem(user['full_name'] or '-'))
            self.user_table.setItem(row, 3, QTableWidgetItem(user['email'] or '-'))
            self.user_table.setItem(row, 4, QTableWidgetItem(user['role'].title()))
            
            # Status with color
            status_item = QTableWidgetItem("Active" if user['is_active'] else "Inactive")
            if user['is_active']:
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item.setForeground(Qt.red)
            self.user_table.setItem(row, 5, status_item)
            
            # Last login
            last_login = user.get('last_login', 'Never')
            if last_login and last_login != 'Never':
                try:
                    dt = datetime.fromisoformat(last_login)
                    last_login = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            self.user_table.setItem(row, 6, QTableWidgetItem(last_login))
        
        self.update_statistics()
        
    def update_statistics(self):
        """Update user statistics"""
        total = self.user_table.rowCount()
        active = sum(1 for row in range(total) 
                    if self.user_table.item(row, 5).text() == "Active")
        admins = sum(1 for row in range(total)
                    if self.user_table.item(row, 4).text() == "Admin")
        
        self.lbl_total_users.setText(f"Total Users: {total}")
        self.lbl_active_users.setText(f"Active Users: {active}")
        self.lbl_admin_users.setText(f"Administrators: {admins}")
        
    def on_selection_changed(self):
        """Handle row selection"""
        has_selection = len(self.user_table.selectedItems()) > 0
        
        self.btn_edit_user.setEnabled(has_selection)
        self.btn_delete_user.setEnabled(has_selection)
        self.btn_reset_password.setEnabled(has_selection)
        self.btn_toggle_status.setEnabled(has_selection)
        
    def get_selected_user(self):
        """Get currently selected user"""
        selected_rows = self.user_table.selectedIndexes()
        if not selected_rows:
            return None
            
        row = selected_rows[0].row()
        return {
            'id': int(self.user_table.item(row, 0).text()),
            'username': self.user_table.item(row, 1).text(),
            'full_name': self.user_table.item(row, 2).text(),
            'email': self.user_table.item(row, 3).text(),
            'role': self.user_table.item(row, 4).text().lower(),
            'is_active': self.user_table.item(row, 5).text() == "Active"
        }
        
    def add_user(self):
        """Add new user"""
        dialog = AddEditUserDialog(self.auth_manager, parent=self)
        
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            user_data = dialog.get_user_data()
            
            try:
                success = self.auth_manager.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    role=user_data['role'],
                    full_name=user_data['full_name'],
                    email=user_data['email']
                )
                
                if success:
                    QMessageBox.information(self, "Success", "User created successfully")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create user")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create user: {str(e)}")
                
    def edit_user(self):
        """Edit selected user"""
        user = self.get_selected_user()
        if not user:
            return
            
        # Prevent editing own account role
        if user['username'] == self.current_user:
            QMessageBox.warning(
                self, "Warning",
                "Cannot edit your own account from this dialog"
            )
            return
            
        dialog = AddEditUserDialog(self.auth_manager, user_data=user, parent=self)
        
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_user_data()
            
            try:
                # Update user in database
                success = self.auth_manager.update_user(
                    user_id=user['id'],
                    full_name=updated_data['full_name'],
                    email=updated_data['email'],
                    role=updated_data['role']
                )
                
                if success:
                    QMessageBox.information(self, "Success", "User updated successfully")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update user")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update user: {str(e)}")
                
    def delete_user(self):
        """Delete selected user"""
        user = self.get_selected_user()
        if not user:
            return
            
        # Prevent deleting own account
        if user['username'] == self.current_user:
            QMessageBox.warning(self, "Warning", "Cannot delete your own account")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete user '{user['username']}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.auth_manager.delete_user(user['id'])
                
                if success:
                    QMessageBox.information(self, "Success", "User deleted successfully")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete user")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
                
    def reset_password(self):
        """Reset user password"""
        user = self.get_selected_user()
        if not user:
            return
            
        new_password, ok = QInputDialog.getText(
            self, "Reset Password",
            f"Enter new password for '{user['username']}':",
            QLineEdit.Password
        )
        
        if ok and new_password:
            confirm_password, ok = QInputDialog.getText(
                self, "Confirm Password",
                "Confirm new password:",
                QLineEdit.Password
            )
            
            if ok:
                if new_password != confirm_password:
                    QMessageBox.warning(self, "Error", "Passwords do not match")
                    return
                    
                if len(new_password) < 6:
                    QMessageBox.warning(
                        self, "Error",
                        "Password must be at least 6 characters"
                    )
                    return
                    
                try:
                    success = self.auth_manager.reset_password(
                        user['username'], new_password
                    )
                    
                    if success:
                        QMessageBox.information(
                            self, "Success",
                            "Password reset successfully"
                        )
                    else:
                        QMessageBox.warning(self, "Error", "Failed to reset password")
                        
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error",
                        f"Failed to reset password: {str(e)}"
                    )
                    
    def toggle_status(self):
        """Toggle user active status"""
        user = self.get_selected_user()
        if not user:
            return
            
        # Prevent deactivating own account
        if user['username'] == self.current_user:
            QMessageBox.warning(self, "Warning", "Cannot deactivate your own account")
            return
            
        new_status = not user['is_active']
        status_text = "activate" if new_status else "deactivate"
        
        reply = QMessageBox.question(
            self, "Confirm Status Change",
            f"Are you sure you want to {status_text} user '{user['username']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.auth_manager.toggle_user_status(
                    user['id'], new_status
                )
                
                if success:
                    QMessageBox.information(
                        self, "Success",
                        f"User {status_text}d successfully"
                    )
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to change status")
                    
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to change status: {str(e)}"
                )


class AddEditUserDialog(QDialog):
    """Dialog for adding/editing user"""
    
    def __init__(self, auth_manager, user_data=None, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.user_data = user_data
        self.is_edit = user_data is not None
        
        self.setWindowTitle("Edit User" if self.is_edit else "Add User")
        self.setMinimumWidth(400)
        
        self.init_ui()
        
        if self.is_edit:
            self.load_user_data()
            
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.txt_username = QLineEdit()
        self.txt_username.setEnabled(not self.is_edit)  # Can't change username
        username_layout.addWidget(self.txt_username)
        
        # Password (only for new users)
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setEnabled(not self.is_edit)
        password_layout.addWidget(self.txt_password)
        
        # Full name
        fullname_layout = QHBoxLayout()
        fullname_layout.addWidget(QLabel("Full Name:"))
        self.txt_fullname = QLineEdit()
        fullname_layout.addWidget(self.txt_fullname)
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.txt_email = QLineEdit()
        email_layout.addWidget(self.txt_email)
        
        # Role
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Role:"))
        self.combo_role = QComboBox()
        self.combo_role.addItems(["user", "investigator", "admin"])
        role_layout.addWidget(self.combo_role)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        
        self.btn_save.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        
        # Add all to layout
        layout.addLayout(username_layout)
        if not self.is_edit:
            layout.addLayout(password_layout)
        layout.addLayout(fullname_layout)
        layout.addLayout(email_layout)
        layout.addLayout(role_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def load_user_data(self):
        """Load existing user data"""
        if self.user_data:
            self.txt_username.setText(self.user_data['username'])
            self.txt_fullname.setText(self.user_data.get('full_name', ''))
            self.txt_email.setText(self.user_data.get('email', ''))
            self.combo_role.setCurrentText(self.user_data['role'])
            
    def validate_input(self):
        """Validate user input"""
        if not self.txt_username.text().strip():
            QMessageBox.warning(self, "Validation Error", "Username is required")
            return False
            
        if not self.is_edit and not self.txt_password.text():
            QMessageBox.warning(self, "Validation Error", "Password is required")
            return False
            
        if not self.is_edit and len(self.txt_password.text()) < 6:
            QMessageBox.warning(
                self, "Validation Error",
                "Password must be at least 6 characters"
            )
            return False
            
        return True
        
    def save(self):
        """Save user"""
        if self.validate_input():
            self.accept()
            
    def get_user_data(self):
        """Get user data from form"""
        return {
            'username': self.txt_username.text().strip(),
            'password': self.txt_password.text() if not self.is_edit else None,
            'full_name': self.txt_fullname.text().strip(),
            'email': self.txt_email.text().strip(),
            'role': self.combo_role.currentText()
        }