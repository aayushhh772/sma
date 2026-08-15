import sqlite3
from datetime import datetime, date

DB_NAME = "attendance_system.db"


def init_db():
    """Creates the SQLite database file and tables automatically if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Master list supporting up to 2 linear/horizontal barcodes per student
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            secondary_barcode TEXT UNIQUE
        )
    """)

    # Attendance log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
            scanned_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, date)
        )
    """)
    conn.commit()
    conn.close()


# Run schema setup automatically on module load
init_db()


def register_student(student_id: str, name: str, secondary_barcode: str = None):
    """Manually link primary and optional secondary barcodes to a student name."""
    student_id = student_id.strip()
    name = name.strip()
    secondary = secondary_barcode.strip() if secondary_barcode else None

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (student_id, name, secondary_barcode) VALUES (?, ?, ?)",
            (student_id, name, secondary)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def process_scan(scanned_code: str):
    """Processes a scan using either barcode, saving 'Present' to attendance_system.db."""
    scanned_code = scanned_code.strip()
    if not scanned_code:
        return

    today_date = date.today().isoformat()
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Search by primary student_id OR secondary_barcode
    cursor.execute("""
        SELECT student_id, name FROM students 
        WHERE student_id = ? OR secondary_barcode = ?
    """, (scanned_code, scanned_code))

    student = cursor.fetchone()

    # Auto-register barcode if unlisted
    if not student:
        student_id = scanned_code
        default_name = f"User_{scanned_code}"
        cursor.execute(
            "INSERT INTO students (student_id, name) VALUES (?, ?)",
            (student_id, default_name)
        )
        conn.commit()
    else:
        student_id = student[0]

    # Insert into attendance table
    try:
        cursor.execute("""
            INSERT INTO attendance (student_id, date, status, scanned_at)
            VALUES (?, ?, 'Present', ?)
        """, (student_id, today_date, now_time))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ignore duplicate scans on the same day

    conn.close()
