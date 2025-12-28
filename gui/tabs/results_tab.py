# gui/tabs/results_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QDialog, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime

class MatchDetailsDialog(QDialog):
    def __init__(self, match, db, parent=None):

        super().__init__(parent)
        self.match = match
        self.db = db
        self.setWindowTitle("Match Details")
        self.setGeometry(200, 200, 700, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        criminal = self.match['criminal']
        
        info_text = f"""
        <b>Criminal Information:</b><br>
        ID: {criminal[1]}<br>
        Name: {criminal[2]}<br>
        Age: {criminal[3] or 'N/A'}<br>
        Height: {criminal[4] or 'N/A'}<br>
        Charges: {criminal[6]}<br>
        Status: {criminal[8]}<br>
        Case #: {criminal[9] or 'N/A'}<br>
        Jurisdiction: {criminal[10] or 'N/A'}<br>
        <br>
        <b>Match Information:</b><br>
        Similarity: <span style='color: green; font-weight: bold;'>{self.match['similarity']:.2f}%</span><br>
        Confidence: {'High' if self.match['similarity'] > 70 else 'Medium' if self.match['similarity'] > 60 else 'Low'}<br>
        Match Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        layout.addWidget(QLabel(info_text))
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class MatchResultsTab(QWidget):
    def __init__(self, db, export_manager, user):
        super().__init__()
        self.db = db
        self.export_manager = export_manager
        self.user = user 
        self.current_matches = []
        self.init_ui()  
        
    def init_ui(self): 
        layout = QVBoxLayout()
        
        # Title and Export button row
        title_layout = QHBoxLayout()
        title = QLabel("Face Recognition Match Results")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # Export button (new feature!)
        export_btn = QPushButton("📄 Export Results")
        export_btn.clicked.connect(self.export_current_results)
        title_layout.addWidget(export_btn)
        
        layout.addLayout(title_layout)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Criminal Name', 'ID', 'Similarity', 
                                              'Case #', 'Charges', 'Actions'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def export_current_results(self): 
        """Export current match results"""
        if not self.current_matches:
            QMessageBox.warning(self, "No Results", "No match results to export!")
            return
        
        try:
            filepath = self.export_manager.export_match_results(
                self.current_matches, 
                self.user
            )
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Results exported to:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Export Failed", 
                f"Failed to export results:\n{str(e)}"
            )
    
    def display_results(self, matches): 
        self.current_matches = matches
        self.table.setRowCount(len(matches))
    
        for row, match in enumerate(matches):

            if 'criminal' in match:
                criminal = match['criminal']
                name = criminal[2]
                criminal_id = criminal[1]
                case_number = criminal[9] or 'N/A'
                charges = criminal[6]
                similarity = match['similarity']
            else:
                name = match['name']
                criminal_id = match['criminal_code']
                case_number = match.get('case_number', 'N/A')
                charges = match['charges']
                similarity = match['similarity']
            
            # Criminal name
            name_item = QTableWidgetItem(name)
            self.table.setItem(row, 0, name_item)
            
            # ID
            id_item = QTableWidgetItem(criminal_id)
            self.table.setItem(row, 1, id_item)
            
            # Similarity (with color coding)
            sim_item = QTableWidgetItem(f"{similarity:.2f}%")
            if similarity > 75:
                sim_item.setBackground(Qt.green)
            elif similarity > 60:
                sim_item.setBackground(Qt.yellow)
            else:
                sim_item.setBackground(Qt.red)
            self.table.setItem(row, 2, sim_item)
            
            # Case #
            case_item = QTableWidgetItem(case_number)
            self.table.setItem(row, 3, case_item)
            
            # Charges (truncate if too long)
            charges_display = charges[:50] + '...' if len(charges) > 50 else charges
            charges_item = QTableWidgetItem(charges_display)
            self.table.setItem(row, 4, charges_item)
            
            # Details button
            details_btn = QPushButton("View Details")
            details_btn.clicked.connect(lambda checked, m=match: self.show_details(m))
            self.table.setCellWidget(row, 5, details_btn)
    
    def show_details(self, match):
        if 'criminal' not in match:
            criminal = self.db.get_criminal_by_id(match['criminal_id'])
            if criminal:
                match['criminal'] = criminal
            else:
                QMessageBox.warning(self, "Error", "Could not load criminal details")
                return
        
        dialog = MatchDetailsDialog(match, self.db, self)
        dialog.exec_()