

# Sibyl - Student Information System

> A modern **Student Information System** inspired by *Psycho-Pass*, with seamless **Dark/Light** mode support and an intuitive management interface.

---

## Overview

**Sibyl** is a powerful yet user-friendly Student Information System designed to streamline the management of student records, collegiate programs, and academic data. With system-aware theme detection, intuitive right-click editing, and comprehensive database views, Sibyl provides an elegant solution for educational data management.

### Key Highlights

✨ **Theme-Aware UI** — Automatically adapts to your system's Dark/Light mode preference  
🎯 **Intuitive Interface** — Right-click context menus for quick record management  
📊 **Comprehensive Views** — Multiple perspectives of student, college, and program data  
🔧 **Easy Editing** — Inline editing with ID-based student lookup  
🎨 **Modern Design** — Clean, professional interface built with modern Python UI libraries

## ✨ Features

### 👥 Student Management
- **Add** new students with required information
- **Edit** existing student records by ID number
- **Delete** student entries with confirmation
- Right-click context menu for quick access to edit/delete actions

### 🏫 College & Program Management
- View comprehensive list of colleges with codes and full names
- Add new colleges and programs via intuitive dialogs
- Manage academic programs within each college
- Right-click editing and deletion for colleges and programs

### 📈 Database & Analytics
- View aggregated student statistics
- Display complete student records in table format
- Access detailed individual student information windows
- Full CRUD operations (Create, Read, Update, Delete) on all records

### 🎨 User Experience
- **System Theme Detection** — Automatically follows OS dark/light mode preference
- **Modern Styling** — Professional UI powered by PyQt6 with custom stylesheets
- **Responsive Design** — Clean, intuitive layout across all pages
- **Data Visualization** — Interactive charts and graphs using matplotlib
- **Audio Feedback** — Sound effects for user interactions
---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows OS (currently optimized for Windows)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/stebbn/Sibyl-SQL.git
cd Sibyl-SQL
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

---

```
Sibyl-SQL/
├── main.py                 # Application entry point
├── README.md              # This file
├── data/
│   └── settings.json      # Configuration and settings
├── modules/
│   ├── appFileHandler.py  # File and data operations
│   ├── DataSQL.py         # Database layer and queries
│   ├── Settings.py        # Settings management
│   ├── Style.py           # UI styling and theming
│   └── utils.py           # Utility functions
├── ui/
│   ├── Sidebar.py         # Navigation sidebar
│   ├── Pages/
│   │   ├── CollegePage.py # College and program management
│   │   ├── DataPage.py    # Database and analytics view
│   │   ├── SettingsPage.py # Application settings
│   │   ├── StatsPage.py   # Statistics dashboard
│   │   └── StudentDataWindow.py # Student details view
│   └── Assets/
│       ├── APP_ICON.ico   # Application icon
│       └── Sounds/        # Audio assets
└── util_seeder.py         # Database seeding utility
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **UI Framework** | PyQt6 |
| **Database** | SQLite |
| **Theme Detection** | `darkdetect` |
| **Data Visualization** | `matplotlib` |
| **Image Processing** | Pillow (PIL) |
| **Audio** | pygame |
| **Packaging** | PyInstaller |
| **Language** | Python 3.8+ |

---

## ⚙️ Configuration

Configuration settings are stored in `data/settings.json`. You can customize:
- Application appearance and theming
- Database connection parameters (if using external DB)
- UI preferences and defaults
- Other application-specific settings

---

## 📝 Usage

1. **Launching the Application:**
   - Run `python main.py` or execute the compiled executable
   - The app automatically detects your system theme

2. **Managing Students:**
   - Navigate to the "Student" page
   - Use the form to add new students
   - Right-click on any student record to edit or delete

3. **Managing Colleges & Programs:**
   - Visit the "College" page
   - Click **+** to add new colleges or programs
   - Right-click for edit/delete options

4. **Viewing Data:**
   - Access the "Data" page for comprehensive database views
   - Check the "Stats" page for aggregate statistics
   - Use "Settings" to configure the application

---

## 🎨 Theming

Sibyl automatically detects and applies your system's theme preference:

- **Light Mode** — Clean, bright interface optimized for daytime use
- **Dark Mode** — Easy on the eyes with dark backgrounds and light text

No manual theme switching needed—the app adapts in real-time!

---

## 🌟 Inspiration

Inspired by the systematic design and aesthetic of *Psycho-Pass*, Sibyl brings structure, order, and intelligent organization to student information management.

---


## 📞 Support

For issues, suggestions, or contributions, please visit the [GitHub repository](https://github.com/stebbn/Sibyl-SQL).

Happy managing! 🎓
