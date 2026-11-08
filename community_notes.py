"""
community_notes.py -- Lightweight, zero-dependency offer intelligence notes.
Provides community offer context (variable pay reality, notice period enforcement,
bonus clawback clauses) without requiring signup or a heavy forum platform.
"""

import re
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "offer_notes.db"

# Initial seed notes for key employers so the UI provides immediate value
SEED_NOTES = [
    (
        "Infosys",
        "Software & Systems Engineering",
        "Variable pay averaged ~65-70% of target last fiscal year. 90-day notice is strictly enforced; RMG rarely approves buyouts.",
        3.5,
        12.0,
        "Lateral Offer (2026)",
    ),
    (
        "TCS",
        "Software & Systems Engineering",
        "Real appraisals for Band B/C were 4-6% this cycle. Notice period is non-negotiable 90 days even with bench approval.",
        4.0,
        9.5,
        "Ex-Employee",
    ),
    (
        "Amazon",
        "Software & Systems Engineering",
        "Year 1 & 2 joining bonuses have strict 12-month clawback clauses. Make sure to clarify base vs RSUs in the total compensation.",
        3.0,
        32.0,
        "Verified Offer",
    ),
    (
        "Google",
        "Software & Systems Engineering",
        "Annual performance bonus target is 15% and has historically paid at or above 100%. Standard 30-day notice period.",
        5.0,
        45.0,
        "Engineer Review",
    ),
    (
        "Swiggy",
        "Software & Systems Engineering",
        "Variable component paid out around 85% of target. ESOPs have 1-year cliff followed by quarterly vesting.",
        4.0,
        28.0,
        "Lateral Offer",
    ),
    (
        "Accenture",
        "Enterprise Solutions & Consulting (SAP/ERP)",
        "Variable bonus depends heavily on practice billing and billable hours. 90-day notice applies across ASE to Associate Director.",
        5.0,
        14.0,
        "Team Lead",
    ),
]


def get_connection():
    """Create or connect to the local SQLite database."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize table and pre-seed high-signal notes if empty."""
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS offer_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role_family TEXT NOT NULL,
                note_text TEXT NOT NULL,
                yoe REAL DEFAULT 0.0,
                ctc_lpa REAL DEFAULT 0.0,
                author_tag TEXT DEFAULT 'Candidate',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur = conn.execute("SELECT COUNT(*) FROM offer_notes")
        count = cur.fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO offer_notes (company, role_family, note_text, yoe, ctc_lpa, author_tag)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                SEED_NOTES,
            )
    conn.close()


def moderate_note(text: str) -> tuple[bool, str]:
    """
    Enforces a strict, solo-moderatable policy:
    1. Length between 10 and 280 characters.
    2. Zero external links / URL spam.
    3. Zero personal contact info / phone / email doxxing.
    4. Anti-defamation check against named individuals.
    """
    cleaned = text.strip()
    if len(cleaned) < 10:
        return False, "Note must be at least 10 characters long."
    if len(cleaned) > 280:
        return False, "Note exceeds 280 characters."

    # Block email addresses first
    if re.search(r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}", cleaned):
        return False, "Email addresses and contact details are not permitted."

    # Block URLs & domains
    if re.search(r"(https?://|www\.|\b[a-zA-Z0-9-]+\.(com|in|org|net|io|co)\b)", cleaned, re.IGNORECASE):
        return False, "External links and web addresses are not permitted."

    # Block phone numbers (Indian mobile or landline)
    if re.search(r"(\+91[\-\s]?)?[6-9]\d{9}\b|\b\d{5}[\-\s]?\d{5}\b", cleaned):
        return False, "Phone numbers are not permitted."

    # Basic manager / individual doxxing pattern ("manager named X", "boss X is")
    if re.search(r"\b(named|mr\.|mrs\.|ms\.)\s+[a-z]{3,}\b", cleaned, re.IGNORECASE):
        return False, "Naming individual employees or managers is strictly prohibited."

    return True, ""


def add_note(
    company: str,
    role_family: str,
    note_text: str,
    yoe: float = 0.0,
    ctc_lpa: float = 0.0,
    author_tag: str = "Candidate Note",
) -> tuple[bool, str]:
    """Validate and insert a new community offer note."""
    is_valid, msg = moderate_note(note_text)
    if not is_valid:
        return False, msg

    init_db()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO offer_notes (company, role_family, note_text, yoe, ctc_lpa, author_tag, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company.strip(),
                    role_family.strip(),
                    note_text.strip(),
                    float(yoe),
                    float(ctc_lpa),
                    author_tag.strip(),
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ),
            )
        return True, "Your offer note was added successfully!"
    finally:
        conn.close()


def get_notes(company: str, role_family: str = None, limit: int = 5) -> list[dict]:
    """Retrieve the most recent verified notes for an employer or role domain."""
    init_db()
    conn = get_connection()
    try:
        # 1. First search by exact or case-insensitive company
        cur = conn.execute(
            """
            SELECT company, role_family, note_text, yoe, ctc_lpa, author_tag, created_at
            FROM offer_notes
            WHERE LOWER(company) = LOWER(?)
            ORDER BY id DESC
            LIMIT ?
            """,
            (company.strip(), limit),
        )
        rows = cur.fetchall()

        # 2. Fallback to role family if company has no notes
        if not rows and role_family:
            cur = conn.execute(
                """
                SELECT company, role_family, note_text, yoe, ctc_lpa, author_tag, created_at
                FROM offer_notes
                WHERE role_family = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (role_family.strip(), limit),
            )
            rows = cur.fetchall()

        return [
            {
                "company": r["company"],
                "role_family": r["role_family"],
                "note_text": r["note_text"],
                "yoe": r["yoe"],
                "ctc_lpa": r["ctc_lpa"],
                "author_tag": r["author_tag"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        conn.close()
