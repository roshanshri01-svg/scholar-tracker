import sqlite3
import os
from datetime import date, timedelta

DB_NAME = "scholarships.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


def get_db_connection():
    """Create and return a database connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed initial sample data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_name TEXT NOT NULL,
            provider TEXT NOT NULL,
            description TEXT,
            eligibility TEXT,
            amount REAL,
            deadline TEXT NOT NULL,
            application_link TEXT,
            application_status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    # Check if table already has data
    cursor.execute("SELECT COUNT(*) as count FROM scholarships")
    row = cursor.fetchone()
    if row and row["count"] == 0:
        seed_sample_data(cursor)
        conn.commit()

    conn.close()


def seed_sample_data(cursor):
    """Seed sample scholarship records with realistic deadlines relative to today."""
    today = date.today()

    sample_scholarships = [
        (
            "Global Leaders STEM Fellowship",
            "TechFuture Foundation",
            "A prestigious fellowship supporting outstanding undergraduate students pursuing degrees in Computer Science, Data Science, and Engineering. Includes mentorship from senior tech leaders and an annual research stipend.",
            "Undergraduate students majoring in STEM fields with a minimum GPA of 3.5. Demonstrated leadership experience or innovative community tech projects.",
            10000.00,
            (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "https://www.techfuturefoundation.org/apply",
            "Pending",
        ),
        (
            "Women in Technology & AI Award",
            "Ada Lovelace Institute",
            "Dedicated to bridging the gender gap in tech by funding female university students specializing in Artificial Intelligence, Cybersecurity, and Software Engineering.",
            "Female students enrolled in an accredited undergraduate or postgraduate computing degree. Minimum 3.2 GPA.",
            7500.00,
            (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            "https://www.adalovelaceinstitute.org/scholarship",
            "Applied",
        ),
        (
            "National Academic Excellence Scholarship",
            "Higher Education Trust",
            "Merit-based financial aid designed to support students across all disciplines who demonstrate superior academic achievements and community engagement.",
            "Enrolled undergraduate students with minimum 3.7 GPA and documented extracurricular leadership.",
            5000.00,
            (today + timedelta(days=28)).strftime("%Y-%m-%d"),
            "https://www.higheredtrust.gov/national-excellence",
            "Pending",
        ),
        (
            "Future Innovators Research Grant",
            "Apex Research Foundation",
            "Funding undergraduate and graduate researchers working on clean energy, sustainable agriculture, and climate resilience technologies.",
            "Full-time university students conducting faculty-supervised scientific research. Proposal submission required.",
            12000.00,
            (today + timedelta(days=45)).strftime("%Y-%m-%d"),
            "https://www.apexresearch.org/grants/future-innovators",
            "Approved",
        ),
        (
            "First-Generation College Achievers Grant",
            "Pathways to Success Council",
            "Designed to alleviate financial barriers for first-generation university students with demonstrated financial need and strong career ambitions.",
            "First in immediate family to attend university. Household income within federal Pell eligibility thresholds.",
            4000.00,
            (today + timedelta(days=60)).strftime("%Y-%m-%d"),
            "https://www.pathwaystosuccess.org/firstgen",
            "Pending",
        ),
        (
            "Civic Leadership & Community Impact Grant",
            "Civic Action Network",
            "Recognizes students who have dedicated at least 150 hours to community service and social advocacy in their local neighborhoods.",
            "Undergraduate or graduate students with proven record of volunteer service or community organizing.",
            3500.00,
            (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "https://www.civicactionnetwork.org/apply",
            "Rejected",
        ),
        (
            "Global Horizons International Scholars Award",
            "Global Education Exchange",
            "Supports students participating in recognized study-abroad programs, international research exchanges, or foreign language immersion.",
            "Students accepted into an approved international academic exchange program. Minimum 3.0 GPA.",
            8500.00,
            (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "https://www.globalhorizons.org/scholars",
            "Applied",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO scholarships (
            scholarship_name, provider, description, eligibility,
            amount, deadline, application_link, application_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_scholarships,
    )


def enrich_scholarship(row):
    """
    Convert SQLite Row to dictionary and compute deadline status & days remaining.
    """
    if not row:
        return None

    item = dict(row)
    today = date.today()

    try:
        deadline_date = date.fromisoformat(item["deadline"])
        days_left = (deadline_date - today).days

        item["days_left"] = days_left
        item["deadline_formatted"] = deadline_date.strftime("%b %d, %Y")

        if days_left < 0:
            item["deadline_status"] = "Expired"
            item["deadline_badge"] = "danger"
            item["deadline_label"] = f"Expired {abs(days_left)} days ago"
        elif days_left == 0:
            item["deadline_status"] = "Due Today"
            item["deadline_badge"] = "danger"
            item["deadline_label"] = "Closes Today!"
        elif days_left <= 7:
            item["deadline_status"] = "Closing Soon"
            item["deadline_badge"] = "warning"
            item["deadline_label"] = f"{days_left} day{'s' if days_left > 1 else ''} left"
        else:
            item["deadline_status"] = "Upcoming"
            item["deadline_badge"] = "success"
            item["deadline_label"] = f"{days_left} days left"
    except (ValueError, TypeError):
        item["days_left"] = None
        item["deadline_formatted"] = item["deadline"]
        item["deadline_status"] = "Unknown"
        item["deadline_badge"] = "secondary"
        item["deadline_label"] = "Date unknown"

    # Status color helper
    status_colors = {
        "Pending": "warning",
        "Applied": "info",
        "Approved": "success",
        "Rejected": "secondary",
    }
    item["status_badge"] = status_colors.get(item.get("application_status", "Pending"), "secondary")

    return item


def get_all_scholarships(search=None, status=None, deadline_type=None, sort_by=None):
    """Fetch scholarships matching search and filter criteria."""
    conn = get_db_connection()
    today_str = date.today().strftime("%Y-%m-%d")

    query = "SELECT * FROM scholarships WHERE 1=1"
    params = []

    if search:
        search_param = f"%{search.strip()}%"
        query += " AND (scholarship_name LIKE ? OR provider LIKE ? OR description LIKE ?)"
        params.extend([search_param, search_param, search_param])

    if status and status != "All":
        query += " AND application_status = ?"
        params.append(status)

    if deadline_type == "upcoming":
        query += " AND deadline >= ?"
        params.append(today_str)
    elif deadline_type == "expired":
        query += " AND deadline < ?"
        params.append(today_str)
    elif deadline_type == "urgent":
        urgent_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
        query += " AND deadline >= ? AND deadline <= ?"
        params.extend([today_str, urgent_date])

    # Sorting
    if sort_by == "deadline_desc":
        query += " ORDER BY deadline DESC"
    elif sort_by == "amount_desc":
        query += " ORDER BY amount DESC"
    elif sort_by == "amount_asc":
        query += " ORDER BY amount ASC"
    elif sort_by == "name_asc":
        query += " ORDER BY scholarship_name ASC"
    elif sort_by == "created_desc":
        query += " ORDER BY created_at DESC"
    else:
        # Default: deadline ascending (urgent first)
        query += " ORDER BY deadline ASC"

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [enrich_scholarship(row) for row in rows]


def get_scholarship_by_id(scholarship_id):
    """Retrieve a single scholarship by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship_id,))
    row = cursor.fetchone()
    conn.close()
    return enrich_scholarship(row)


def add_scholarship(name, provider, description, eligibility, amount, deadline, link, status):
    """Insert a new scholarship record using parameterized query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO scholarships (
            scholarship_name, provider, description, eligibility,
            amount, deadline, application_link, application_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, provider, description, eligibility, amount, deadline, link, status),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_scholarship(scholarship_id, name, provider, description, eligibility, amount, deadline, link, status):
    """Update an existing scholarship record using parameterized query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE scholarships
        SET scholarship_name = ?,
            provider = ?,
            description = ?,
            eligibility = ?,
            amount = ?,
            deadline = ?,
            application_link = ?,
            application_status = ?
        WHERE id = ?
        """,
        (name, provider, description, eligibility, amount, deadline, link, status, scholarship_id),
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def update_scholarship_status(scholarship_id, new_status):
    """Update only the application status of a scholarship."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE scholarships SET application_status = ? WHERE id = ?",
        (new_status, scholarship_id),
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def delete_scholarship(scholarship_id):
    """Delete a scholarship record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scholarship_name FROM scholarships WHERE id = ?", (scholarship_id,))
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        return None

    deleted_name = existing["scholarship_name"]
    cursor.execute("DELETE FROM scholarships WHERE id = ?", (scholarship_id,))
    conn.commit()
    conn.close()
    return deleted_name


def get_dashboard_data():
    """Calculate and return all statistics required for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    urgent_limit = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    # Total count and total funding amount
    cursor.execute("SELECT COUNT(*) as total_count, COALESCE(SUM(amount), 0) as total_amount FROM scholarships")
    total_stats = cursor.fetchone()
    total_count = total_stats["total_count"]
    total_amount = total_stats["total_amount"]

    # Upcoming vs Expired
    cursor.execute("SELECT COUNT(*) as count FROM scholarships WHERE deadline >= ?", (today_str,))
    upcoming_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM scholarships WHERE deadline < ?", (today_str,))
    expired_count = cursor.fetchone()["count"]

    # Approaching deadlines (closing within 7 days)
    cursor.execute(
        "SELECT COUNT(*) as count FROM scholarships WHERE deadline >= ? AND deadline <= ?",
        (today_str, urgent_limit),
    )
    urgent_count = cursor.fetchone()["count"]

    # Status counts
    cursor.execute("SELECT application_status, COUNT(*) as count FROM scholarships GROUP BY application_status")
    status_rows = cursor.fetchall()
    status_counts = {"Pending": 0, "Applied": 0, "Approved": 0, "Rejected": 0}
    for row in status_rows:
        if row["application_status"] in status_counts:
            status_counts[row["application_status"]] = row["count"]

    # Approaching deadlines list (next 5 upcoming deadlines)
    cursor.execute(
        "SELECT * FROM scholarships WHERE deadline >= ? ORDER BY deadline ASC LIMIT 5",
        (today_str,),
    )
    approaching_rows = cursor.fetchall()
    approaching = [enrich_scholarship(r) for r in approaching_rows]

    # Recently added scholarships (last 5 created)
    cursor.execute("SELECT * FROM scholarships ORDER BY created_at DESC, id DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    recently_added = [enrich_scholarship(r) for r in recent_rows]

    conn.close()

    return {
        "total_count": total_count,
        "total_amount": total_amount,
        "upcoming_count": upcoming_count,
        "expired_count": expired_count,
        "urgent_count": urgent_count,
        "status_counts": status_counts,
        "approaching": approaching,
        "recently_added": recently_added,
    }
