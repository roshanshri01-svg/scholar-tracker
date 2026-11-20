# Scholar Track – Scholarship Management System

A web application developed using **Python Flask**, **SQLite**, **HTML5**, **CSS3**, **JavaScript**, and **Bootstrap 5** to help students discover, manage, and track scholarship opportunities, eligibility requirements, application deadlines, and application progress.

---

## 🚀 Key Features

- **Executive Dashboard:** Real-time summary statistics (Total, Upcoming, Closing Soon, Past Deadlines, Potential Aid Value) and interactive application tracking visualizations.
- **Approaching Deadline Alerts:** Automatic calculation of days remaining with visual badges for upcoming, urgent (≤ 7 days), due today, and expired deadlines.
- **Full CRUD Management:** Create, view, update, and safely delete scholarship opportunities with confirmation modals.
- **Multi-Factor Search & Filtering:** Filter by keyword (name, provider, description), application status (`Pending`, `Applied`, `Approved`, `Rejected`), and deadline status (`Upcoming`, `Closing Soon`, `Expired`), with flexible sorting.
- **Quick Status Updates:** Switch application stages on-the-fly directly from the table or detailed view.
- **Responsive Modern UI:** Modern sidebar navigation, clean cards, and responsive layouts optimized for desktops, tablets, and smartphones.
- **Automated Database Setup:** Initializes SQLite database schema and pre-loads sample data automatically on first launch without creating duplicates.

---

## 📁 Project Directory Structure

```text
Scholar Track/
│
├── app.py                      # Flask routes, validations, controllers, and error handlers
├── database.py                 # SQLite database initialization, queries, and calculations
├── requirements.txt            # Python dependencies (Flask)
├── scholarships.db             # Auto-created SQLite database file
├── README.md                   # Setup guide and documentation
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout with responsive sidebar and top navbar
│   ├── index.html              # Main dashboard overview and metrics
│   ├── scholarships.html       # Search, filter, and scholarship directory table
│   ├── add_scholarship.html    # Add new scholarship form
│   ├── edit_scholarship.html   # Edit existing scholarship form
│   ├── scholarship_details.html# Comprehensive detail view with countdown banner
│   ├── 404.html                # Page not found error page
│   └── 500.html                # Internal server error page
│
└── static/                     # Static frontend assets
    ├── css/
    │   └── style.css           # Custom styling, animations, and responsive layout
    └── js/
        └── script.js           # Sidebar toggle, delete modal handler, auto-dismiss alerts
```

---

## 🛠️ Step-by-Step Setup & Execution (Windows in VS Code)

### Step 1: Open Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File** &rarr; **Open Folder...** and select this project directory.
3. Open the built-in terminal by pressing ``Ctrl + ` `` (Backtick) or selecting **Terminal** &rarr; **New Terminal**.

### Step 2: Verify Python Version
Check that Python 3.8+ is installed:
```powershell
python --version
```

### Step 3: Create & Activate Virtual Environment
Create an isolated virtual environment named `venv`:
```powershell
python -m venv venv
```
Activate the environment:
```powershell
venv\Scripts\activate
```
*(If you see an execution policy error in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or activate using Command Prompt `venv\Scripts\activate.bat`)*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Start the Flask Application
```powershell
python app.py
```

### Step 6: View the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 📋 Database Schema (`scholarships` Table)

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Unique identifier for each scholarship |
| `scholarship_name` | `TEXT NOT NULL` | Title / name of the scholarship |
| `provider` | `TEXT NOT NULL` | Organization, university, or donor |
| `description` | `TEXT` | Summary of benefits, terms, and background |
| `eligibility` | `TEXT` | Academic, financial, or prerequisite criteria |
| `amount` | `REAL` | Total financial award amount ($) |
| `deadline` | `TEXT NOT NULL` | Application deadline in `YYYY-MM-DD` format |
| `application_link` | `TEXT` | External URL to official application portal |
| `application_status` | `TEXT NOT NULL DEFAULT 'Pending'` | Stage (`Pending`, `Applied`, `Approved`, `Rejected`) |
| `created_at` | `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` | Timestamp of when the record was created |

---

## ❓ Common Errors & Solutions

1. **`Activate.ps1 cannot be loaded because running scripts is disabled`**
   - **Cause:** Windows PowerShell script execution policy restricts unapproved scripts.
   - **Fix:** In your PowerShell terminal, run:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```
     Or use standard Command Prompt (`cmd`): `venv\Scripts\activate.bat`.

2. **`Address already in use` or Port 5000 occupied**
   - **Cause:** Another process or background server is already running on port 5000.
   - **Fix:** In `app.py`, change `port=5000` to `port=5001` or another open port on the last line: `app.run(debug=True, host="127.0.0.1", port=5001)`.

3. **`ModuleNotFoundError: No module named 'flask'`**
   - **Cause:** The virtual environment is not activated or dependencies were not installed.
   - **Fix:** Run `venv\Scripts\activate` and then `pip install -r requirements.txt`.
