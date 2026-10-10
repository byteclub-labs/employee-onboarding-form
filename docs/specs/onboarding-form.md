# Spec: Single-Page Employee Onboarding Form

### FEATURE SUMMARY

Build a single-page HTML application for employee onboarding: a data-collection form that lets a small organization record the details needed to onboard a new team member, plus a list of employees already onboarded, served by a minimal Python standard-library backend with SQLite persistence. The repository currently contains only a README describing this intent ("Single-page HTML data collection form for new employee joining (small organization)"), so this spec is greenfield; it mirrors the shape of a previous factory attempt on this repo (Python `server.py` + `static/` frontend + SQLite). The feature interacts with nothing else — there is no existing code on `main`.

### USER STORIES

1. As an HR/admin user at a small organization, I want a single web page with a form to enter a new employee's details, so that I can collect onboarding information without any tooling beyond a browser.
2. As an HR/admin user, I want required fields to be clearly marked and validated before submission, so that incomplete records are never saved.
3. As an HR/admin user, I want the employee's record to be persisted server-side when I submit the form, so that onboarding data survives page reloads and is shared across browsers.
4. As an HR/admin user, I want to see a list of employees already onboarded (with a count) on the same page, so that I can confirm a submission worked and review who has been onboarded.
5. As an HR/admin user, I want a clear success confirmation and inline error messages, so that I always know whether a submission succeeded or what to fix.
6. As a developer/operator, I want to run the app with a single `python3 server.py` command and no external dependencies, so that a small organization can run it anywhere Python 3 exists.

### ACCEPTANCE CRITERIA

1. Running `python3 server.py` from the repo root starts a server on port 8000, and `GET http://localhost:8000/` returns an HTML page titled/headed "Employee Onboarding" (HTTP 200). No pip installs or other dependencies are required (Python 3 standard library only).
2. The page renders a form containing these fields: Full name (required, text), Personal email (required, email), Phone (required, tel), Job title (required, text), Department (required, select with options Engineering, Sales, Marketing, HR, Finance, Operations, Other), Start date (required, date), Employment type (required, select with options Full-time, Part-time, Contract), Address (optional, textarea), Emergency contact name (optional, text), Emergency contact phone (optional, tel), Notes (optional, textarea). Required fields are visually marked; optional fields are marked optional.
3. Submitting the form with any required field empty or with an invalid email format does NOT create a record and shows a visible error message identifying the problem (client-side validation prevents the submit; the browser never silently saves bad data).
4. Submitting the form with all required fields valid persists the record and displays it in the "onboarded employees" list on the same page without a manual reload; the form is cleared and a visible success confirmation is shown.
5. `POST /api/employees` with a valid JSON body returns 201 and the created record (including a server-assigned `id` and creation timestamp); `GET /api/employees` returns a JSON array of all stored employees, most recent first.
6. `POST /api/employees` with a missing required field, an invalid email, or an invalid `start_date` (must be a real calendar date, `YYYY-MM-DD`) returns HTTP 400 with a JSON error body and stores nothing.
7. Data is stored in SQLite at `data/onboarding.db` (created automatically on first run and ignored by git); after restarting the server, previously submitted employees are still returned by `GET /api/employees` and rendered in the list.
8. The employees list shows each record's name, job title, department, start date, and employment type, plus a heading/count of total onboarded employees; before any submission it shows a "no employees yet" style empty state (or count of 0).
9. Server-side validation enforces the same required/optional rules, email format, and maximum lengths as the client (e.g. name ≤120 chars, email ≤254, phone ≤40, address ≤240, notes ≤500); requests over 64 KB body are rejected.
10. The layout is a clean single-column card-style page that remains usable at mobile widths (~360 px) and desktop widths: labels above fields, selects/date picker use native controls, and the submit button is prominent.
11. Static assets are served from `static/` (e.g. `/static/styles.css`, `/static/app.js`) and unknown paths return 404 (no path traversal or directory listing).

### SCOPE

IN:
- One HTML page (`static/index.html`) with the onboarding form and onboarded-employees list, styled by `static/styles.css`, behavior in `static/app.js`.
- `server.py` at repo root: Python 3 stdlib HTTP server (port 8000) serving the page, static assets, and a small JSON API (`GET`/`POST /api/employees`).
- SQLite persistence at `data/onboarding.db` via stdlib `sqlite3`; `.gitignore` entry for the data directory/database file.
- Client-side and server-side validation for required fields, email format, start-date format, and field length caps.
- In-page success/error messaging and automatic list refresh after submit.
- README update with run instructions (`python3 server.py`, open http://localhost:8000).

OUT:
- Authentication, user accounts, roles, or access control.
- Editing or deleting employee records (any UI or API for update/delete).
- File/photo uploads, signatures, or document generation.
- Email notifications or integrations with HRIS/payroll systems.
- Automated test suites, CI configuration, Docker, or deployment config.
- Multi-page navigation, wizards, or admin dashboards.
- External dependencies of any kind (frameworks, ORMs, CDNs) — stdlib only.

### OPEN QUESTIONS

NONE — resolved by PO: the form persists to a shared SQLite store rather than localStorage because the README describes organizational data collection; Python 3 stdlib + SQLite mirrors the prior attempt's shape and keeps the app dependency-free; port 8000 and the field set/options follow the prior attempt's conventions; edit/delete/auth are explicitly out of scope for v1.

### STATUS

STATUS: COMPLETE
