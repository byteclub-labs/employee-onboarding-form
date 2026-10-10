#!/usr/bin/env python3
"""Employee Onboarding — single-page data-collection form.

Serves the page and its static assets, a small JSON API under /api/, and
owns the SQLite store. Python 3 standard library only.

Run: python3 server.py  ->  http://localhost:8000
"""

import json
import os
import re
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "data" / "onboarding.db"

MAX_BODY_BYTES = 64 * 1024
MAX_FIELD_LEN = 120
MAX_EMAIL_LEN = 254
MAX_PHONE_LEN = 40
MAX_ADDRESS_LEN = 240
MAX_NOTES_LEN = 500
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

DEPARTMENTS = (
    "Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other",
)
EMPLOYMENT_TYPES = ("Full-time", "Part-time", "Contract")

# Exact-match path -> (file, mime) whitelist; any other path is a 404.
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/static/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/static/app.js": ("app.js", "application/javascript; charset=utf-8"),
}
API_PATHS = {"/api/employees"}
KNOWN_PATHS = set(STATIC_FILES) | API_PATHS

SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  job_title TEXT NOT NULL,
  department TEXT NOT NULL,
  start_date TEXT NOT NULL,
  employment_type TEXT NOT NULL,
  address TEXT NOT NULL DEFAULT '',
  emergency_contact_name TEXT NOT NULL DEFAULT '',
  emergency_contact_phone TEXT NOT NULL DEFAULT '',
  notes TEXT NOT NULL DEFAULT '',
  submitted_at TEXT NOT NULL
);
"""

NOW = "strftime('%Y-%m-%dT%H:%M:%SZ','now')"

FIELDS = (
    "id", "full_name", "email", "phone", "job_title", "department",
    "start_date", "employment_type", "address", "emergency_contact_name",
    "emergency_contact_phone", "notes", "submitted_at",
)
SELECT_SQL = "SELECT " + ", ".join(FIELDS) + " FROM employees"


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)


def _trim(value, limit):
    """Return value as a trimmed string capped at limit, '' for non-strings."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


def _is_date(value):
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _record(row):
    return dict(zip(FIELDS, row))


def handle_create_employee(body):
    """POST /api/employees — insert a new employee onboarding record."""
    full_name = _trim(body.get("full_name"), MAX_FIELD_LEN + 1)
    email_raw = body.get("email")
    email = email_raw.strip().lower() if isinstance(email_raw, str) else ""
    phone = _trim(body.get("phone"), MAX_PHONE_LEN + 1)
    job_title = _trim(body.get("job_title"), MAX_FIELD_LEN + 1)
    department = _trim(body.get("department"), MAX_FIELD_LEN + 1)
    employment_type = _trim(body.get("employment_type"), MAX_FIELD_LEN + 1)
    start_date = _trim(body.get("start_date"), 11)
    address = _trim(body.get("address"), MAX_ADDRESS_LEN + 1)
    emergency_contact_name = _trim(
        body.get("emergency_contact_name"), MAX_FIELD_LEN + 1)
    emergency_contact_phone = _trim(
        body.get("emergency_contact_phone"), MAX_PHONE_LEN + 1)
    notes = _trim(body.get("notes"), MAX_NOTES_LEN + 1)

    if not full_name:
        return 400, {"error": "Full name is required."}
    if len(full_name) > MAX_FIELD_LEN:
        return 400, {"error": "Full name must be 120 characters or fewer."}
    if not email or len(email) > MAX_EMAIL_LEN or not EMAIL_RE.match(email):
        return 400, {"error": "A valid email address is required."}
    if not phone:
        return 400, {"error": "Phone number is required."}
    if len(phone) > MAX_PHONE_LEN:
        return 400, {"error": "Phone number must be 40 characters or fewer."}
    if not job_title:
        return 400, {"error": "Job title is required."}
    if len(job_title) > MAX_FIELD_LEN:
        return 400, {"error": "Job title must be 120 characters or fewer."}
    if department not in DEPARTMENTS:
        return 400, {"error": "Please choose a department from the list."}
    if employment_type not in EMPLOYMENT_TYPES:
        return 400, {"error": "Please choose an employment type from the list."}
    if not DATE_RE.match(start_date) or not _is_date(start_date):
        return 400, {"error": "A valid start date is required."}
    if len(address) > MAX_ADDRESS_LEN:
        return 400, {"error": "Address must be 240 characters or fewer."}
    if len(emergency_contact_name) > MAX_FIELD_LEN:
        return 400, {
            "error": "Emergency contact name must be 120 characters or fewer."}
    if len(emergency_contact_phone) > MAX_PHONE_LEN:
        return 400, {
            "error": "Emergency contact phone must be 40 characters or fewer."}
    if len(notes) > MAX_NOTES_LEN:
        return 400, {"error": "Notes must be 500 characters or fewer."}

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO employees (full_name, email, phone, job_title,"
            " department, employment_type, start_date, address,"
            " emergency_contact_name, emergency_contact_phone, notes,"
            " submitted_at)"
            f" VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, {NOW})",
            (full_name, email, phone, job_title, department,
             employment_type, start_date, address, emergency_contact_name,
             emergency_contact_phone, notes),
        )
        row = conn.execute(
            SELECT_SQL + " WHERE id = ?", (cur.lastrowid,)
        ).fetchone()

    return 201, _record(row)


def list_employees():
    """GET /api/employees — every onboarded employee, newest first."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            SELECT_SQL + " ORDER BY submitted_at DESC, id DESC"
        ).fetchall()
    employees = [_record(row) for row in rows]
    return 200, employees


class OnboardingHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # --- helpers ---------------------------------------------------------

    def _security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'")

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._security_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filename, mime):
        path = STATIC_DIR / filename
        try:
            body = path.read_bytes()
        except OSError:
            self._send_json(404, {"error": "not found"})
            return
        self.send_response(200)
        self._security_headers()
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self):
        """Parse the request body as a JSON object; returns (dict, error)."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length > MAX_BODY_BYTES:
            return None, (400, {"error": "Request body too large."})
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None, (400, {"error": "Request body must be valid JSON."})
        if not isinstance(body, dict):
            return None, (400, {"error": "Request body must be a JSON object."})
        return body, None

    def _reject(self):
        """Wrong method on a known path -> 405; anything else -> 404."""
        if self.path in KNOWN_PATHS:
            allowed = "GET" if self.path in STATIC_FILES else "GET, POST"
            self.send_response(405)
            self._security_headers()
            self.send_header("Allow", allowed)
            body = json.dumps({"error": "method not allowed"}).encode("utf-8")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._send_json(404, {"error": "not found"})

    # --- routes ----------------------------------------------------------

    def do_GET(self):
        if self.path in STATIC_FILES:
            filename, mime = STATIC_FILES[self.path]
            self._send_file(filename, mime)
        elif self.path == "/api/employees":
            status, payload = list_employees()
            self._send_json(status, payload)
        elif self.path in KNOWN_PATHS:
            self._reject()
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/api/employees":
            body, error = self._json_body()
            status, payload = error or handle_create_employee(body)
            self._send_json(status, payload)
        elif self.path in KNOWN_PATHS:
            self._reject()
        else:
            self._send_json(404, {"error": "not found"})

    do_PUT = _reject
    do_PATCH = _reject
    do_DELETE = _reject
    do_HEAD = _reject


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), OnboardingHandler)
    print(f"Employee Onboarding running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
