# Forensic Face Recognition System v2.0

A complete, production-ready forensic face recognition system designed for law enforcement agencies. Features include criminal database management, mugshot capture, suspect recognition, batch processing, real-time recognition, and comprehensive reporting.

## 🌟 Features

### Core Features
- **Criminal Database Management**: Add, edit, search, and manage criminal records
- **Mugshot Capture**: Capture and store criminal mugshots with automatic face encoding
- **Suspect Recognition**: Upload or capture suspect images and search against database
- **Batch Processing**: Process multiple suspect images simultaneously
- **Real-time Camera Recognition**: Live camera feed with real-time face matching
- **Export Reports**: Generate PDF, CSV, and JSON reports

### Security Features
- **Multi-role Authentication**: Admin, Investigating Head, Investigating Officer
- **Role-based Permissions**: Granular access control
- **Activity Logging**: Track all user actions
- **Session Management**: Automatic timeout and lockout after failed attempts

### UI Features
- **Dual Theme Support**: Light and Dark themes
- **Modern Interface**: Clean, professional design
- **Responsive Layout**: Optimized for various screen sizes
- **Image Quality Validation**: Automatic quality checks

## 📋 Requirements

### System Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: 5GB free space
- **Camera**: Built-in or USB webcam
- **Python**: 3.12.7 or higher

### Hardware Requirements
- **CPU**: Intel i5 or equivalent (i7 recommended for batch processing)
- **GPU**: Optional but recommended for faster processing
- **Display**: 1920x1080 minimum resolution

## 🚀 Installation

### Step 1: Install Python
1. Download Python 3.12.7 from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation:
```bash
python --version
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -c "import deepface; print('Success!')"
```

## 🎯 Quick Start

### First Run
```bash
python main.py
```

### Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT**: Change the default password immediately after first login!

## 📖 User Guide

### 1. Login
- Enter your credentials
- System will lock account for 5 minutes after 3 failed attempts

### 2. Criminal Database Tab
#### Adding a Criminal
1. Click "Criminal Database" tab
2. Fill in required fields:
   - Criminal ID (e.g., CR-2024-001)
   - Full Name
   - Charges
3. Optional fields:
   - Age, Height, Physical Description
   - Case Number, Jurisdiction
   - Notes
4. Click "Add Criminal"

#### Searching Criminals
- Use the search bar to find criminals by name, ID, or charges
- Click on a record to view details
- Click "Delete" to remove a record (Admin/Head only)

### 3. Capture Mugshots Tab
#### Capturing a Mugshot
1. Select a criminal from the dropdown
2. Click "Start Camera"
3. Position face in frame (good lighting, clear view)
4. Click "Capture Mugshot"
5. System automatically extracts face encoding
6. Click "Stop Camera" when done

**Tips for Best Results**:
- Ensure good lighting
- Face should be clearly visible
- Look directly at camera
- Remove glasses if possible
- Capture multiple angles

### 4. Suspect Recognition Tab
#### Recognizing a Suspect
**Method 1: Upload Image**
1. Click "Upload Image"
2. Select suspect image file
3. Click "Search for Matches"
4. View results in Match Results tab

**Method 2: Capture from Camera**
1. Click "Capture from Camera"
2. Press SPACE to capture, ESC to cancel
3. Click "Search for Matches"

#### Batch Processing
1. Click "Batch Process" button
2. Select multiple suspect images
3. Monitor progress bar
4. View results for each image

### 5. Real-time Recognition (New!)
1. Navigate to Recognition tab
2. Click "Start Real-time Recognition"
3. Camera feed shows live with match overlays
4. Matches displayed with confidence levels
5. Click "Stop" to end session

### 6. Match Results Tab
#### Viewing Matches
- Matches sorted by similarity (highest first)
- Color-coded by confidence:
  - 🟢 Green: 75%+ (High confidence)
  - 🟡 Yellow: 60-75% (Medium confidence)
  - 🔴 Red: <60% (Low confidence)

#### Match Details
- Click "View Details" for complete information
- View side-by-side comparison
- Export individual match reports

### 7. Export Reports
#### PDF Export
1. Select matches to export
2. Click "Export to PDF"
3. Report includes:
   - Suspect information
   - All matches with details
   - Confidence assessments
   - Official stamps and metadata

#### CSV/JSON Export
- Click "Export to CSV" or "Export to JSON"
- Use for further analysis or integration

### 8. User Management (Admin Only)
1. Go to Settings → User Management
2. Add/Edit/Delete users
3. Assign roles and permissions
4. View activity logs

### 9. Settings
#### Theme Selection
- Settings → Appearance → Theme
- Choose Light or Dark theme
- Changes apply immediately

#### System Configuration
- Settings → System
- Adjust recognition thresholds
- Configure camera settings
- Set export preferences

## 👥 User Roles & Permissions

### Admin
- Full system access
- User management
- System configuration
- All CRUD operations
- Export reports
- View statistics

### Investigating Head
- Add/edit/delete criminals
- Capture mugshots
- Recognize suspects
- Batch processing
- Export reports
- View statistics

### Investigating Officer
- Add criminals (no delete)
- Capture mugshots
- Recognize suspects
- Batch processing
- Export reports
- Limited statistics

## 🔒 Security Best Practices

1. **Change Default Password**: Immediately after installation
2. **Regular Backups**: Backup `data/database.db` regularly
3. **Access Control**: Assign minimum required permissions
4. **Activity Monitoring**: Review activity logs regularly
5. **Secure Storage**: Keep the system on secure, encrypted drives
6. **Network Security**: Use firewall if networked

## 📊 Database Schema

### Tables
- **users**: User accounts and authentication
- **criminals**: Criminal records
- **mugshots**: Criminal mugshots with face encodings
- **suspects**: Suspect images uploaded for recognition
- **matches**: Match results between suspects and criminals
- **login_history**: User login/logout tracking
- **activity_log**: All user actions

## 🛠️ Troubleshooting

### Camera Not Working
```python
# Test camera
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(f"Camera working: {ret}")
cap.release()
```

### Face Not Detected
- Ensure good lighting
- Face should be frontal
- Check if face is large enough in frame
- Verify face is not obscured

### Slow Performance
- Close other applications
- Reduce batch processing thread count
- Use 'hog' detection model instead of 'cnn'
- Consider GPU acceleration

### Database Locked
- Close all other instances
- Check file permissions
- Restart application

### Installation Errors
```bash
# dlib installation failed
pip install cmake
pip install dlib

# OpenCV issues
pip uninstall opencv-python
pip install opencv-python-headless
```

## 📁 Project Structure
```
Forensic-Face-Recognition-System/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── setup.py                        # Installation setup
├── README.md                       
│
├── config/
│   └── config.py                   # Configuration
│
├── database/
│   ├── models.py
│   ├── db_manager.py              # Main database operations
│   └── auth_manager.py            # Authentication
│
├── core/
│   ├── face_recognition_engine.py # Face recognition logic
│   ├── utils.py                   # Utility functions
│   ├── sketch_engine.py
│   ├── export_manager.py          # Report generation
│   └── batch_processor.py         # Batch processing
│
├── gui/
│   ├── main_window.py             # Main window
│   ├── auth/
│   │   └── login_window.py        # Login dialog
│   ├── tabs/
│   │   └──dialogs/
│   │   │   └──user_management_dialogs.py
│   │   ├── criminal_tab.py        # Criminal management
│   │   ├── batch_tab.py
│   │   ├── realtime_tab.py
│   │   ├── mugshot_tab.py         # Mugshot capture
│   │   ├── recognition_tab.py     # Suspect recognition
│   │   ├── results_tab.py         # Match results
│   │   ├── sketch_tab.py
│   │   └── settings_tab.py        # Settings
│   └── styles/
│       └── theme_manager.py       # Theme management
│
└── data/                          
    ├── database.db                # SQLite database
    ├── mugshots/                  # Criminal mugshots
    ├── suspects/                  # Suspect images
    ├── exports/                   # Generated reports
    └── temp/                      # Temporary files
```

## 🔄 Updates & Changelog

### Version 2.0.0 (Current)
- ✅ Multi-user authentication system
- ✅ Role-based access control
- ✅ Batch processing for multiple images
- ✅ Real-time camera recognition
- ✅ PDF/CSV/JSON export
- ✅ Light/Dark theme support
- ✅ Image quality validation
- ✅ Activity logging
- ✅ Enhanced UI/UX

### Version 1.0.0
- Basic face recognition
- Criminal database
- Mugshot capture
- Simple matching

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## ⚠️ Disclaimer

This software is designed for law enforcement and authorized personnel only. Users are responsible for compliance with local laws and regulations regarding biometric data collection and storage.

## 📧 Support

For issues, questions, or feature requests:
- GitHub Issues: [Project Issues](https://github.com/ashus1ngh/forensic-face-recognition/issues)
- Email: ashishkumar.ds003@gmail.com

## 🙏 Acknowledgments

- face_recognition library by Adam Geitgey
- OpenCV community
- PyQt6 developers
- dlib library by Davis King

## 📚 Additional Resources

- [Face Recognition Documentation](https://face-recognition.readthedocs.io/)
- [OpenCV Tutorials](https://docs.opencv.org/master/d9/df8/tutorial_root.html)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

---

**Built with ❤️ for law enforcement agencies**

Version 2.0.0 | Last Updated: 2025