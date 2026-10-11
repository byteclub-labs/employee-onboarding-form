# Spec: Single-Page Employee Onboarding Form

### FEATURE SUMMARY

Build a single-page HTML application for employee onboarding data collection: an admin at a small organization opens one page in a browser, enters a new hire's details into a form, and sees the running list of onboarded employees on the same page, backed by a minimal Python standard-library server with SQLite persistence. The repository's `main` branch contains only a README whose description is this exact feature ("Single-page HTML data collection form for new employee joining (small organization)"), so this is greenfield — there is no existing code to integrate with. The spec mirrors the product shape established by earlier factory attempts on this repo's unmerged branches (`server.py` + `static/` frontend + SQLite + `GET`/`POST /api/employees`). The closest existing feature/pattern is that prior attempt's architecture; the feature interacts with nothing else in the codebase.

### USER STORIES

1. As an HR/admin user at a small organization, I want a single web page with a form to enter a new employee's details, so that I can collect onboarding information in a browser with no extra tooling.
2. As an HR/admin user, I want required fields clearly marked and validated before submission, so that incomplete or malformed records are never saved.
3. As an HR/admin user, I want submitted records persisted on the server, so that onboarding data survives page reloads and is visible from any browser that can reach the server.
4. As an HR/admin user, I want to see a list of employees already onboarded (with a total count) on the same page, so that I can confirm a submission worked and review prior records.
5. As an HR/admin user, I want a clear success confirmation and inline error messages, so that I always know whether a submission succeeded or what to fix.
6. As an operator at a small organization, I want to run the app with a single command (`python3 server.py`) and no external dependencies, so that it can be hosted anywhere Python 3 exists.

### ACCEPTANCE CRITERIA

1. Running `python3 server.py` from the repo root starts a server on port 8000; `GET http://localhost:8000/` returns HTTP 200 with an HTML page titled/headed "Employee Onboarding". No `pip install` or third-party dependency is required — Python 3 standard library only.
2. The page renders a form with these fields: Full name (required, text), Personal email (required, email), Phone (required, tel), Job title (required, text), Department (required, select with options: Engineering, Sales, Marketing, HR, Finance, Operations, Other), Start date (required, date picker), Employment type (required, select with options: Full-time, Part-time, Contract), Address (optional, textarea), Emergency contact name (optional, text), Emergency contact phone (optional, tel), Notes (optional, textarea). Required fields are visibly marked; optional fields are labeled optional.
3. Submitting with any required field empty or with an invalid email does not create a record: client-side validation blocks submission and shows a visible error identifying the problem.
4. Submitting a fully valid form persists the record, clears the form, shows a visible success confirmation, and displays the new record in the onboarded-employees list without a manual page reload.
5. `POST /api/employees` with a valid JSON body returns HTTP 201 with the created record including a server-assigned `id` and `submitted_at` timestamp; `GET /api/employees` returns a JSON array of all stored employees, most recent first.
6. `POST /api/employees` with a missing required field, an invalid email, or an invalid `start_date` (must be a real calendar date in `YYYY-MM-DD`) returns HTTP 400 with a JSON error body and stores nothing.
7. Records are stored in SQLite at `data/onboarding.db`, created automatically on first run and excluded from git via `.gitignore`; after a server restart, previously submitted employees are still returned by `GET /api/employees` and rendered in the list.
8. The employee list shows each record's name, job title, department, start date, and employment type, plus a visible total count of onboarded employees; with zero records it renders an empty state or a count of 0.
9. Server-side validation enforces the same rules as the client: required/optional fields, email format, `start_date` format, and length caps (name ≤ 120 chars, email ≤ 254, phone ≤ 40, job title ≤ 120, address ≤ 240, emergency contact name ≤ 120, emergency contact phone ≤ 40, notes ≤ 500); request bodies over 64 KB are rejected.
10. The layout is a clean single-column card-style page usable at mobile (~360 px) and desktop widths: labels above fields, native controls for selects and the date input, and a prominent submit button.
11. Static assets are served from `static/` (e.g. `/static/styles.css`, `/static/app.js`); unknown paths return HTTP 404 with no directory listing and no path traversal.

### SCOPE

IN:
- One HTML page (`static/index.html`) containing the onboarding form and the onboarded-employees list, styled by `static/styles.css` with behavior in `static/app.js`.
- `server.py` at repo root: a Python 3 stdlib HTTP server on port 8000 serving the page, static assets, and a small JSON API (`GET`/`POST /api/employees`).
- SQLite persistence at `data/onboarding.db` via stdlib `sqlite3`, plus a `.gitignore` entry covering the data directory.
- Client-side and server-side validation for required fields, email format, `start_date` format, and field-length caps.
- In-page success/error messaging and automatic list refresh after submit.
- README update with run instructions (`python3 server.py`, then open http://localhost:8000).

OUT:
- Authentication, user accounts, roles, or access control.
- Editing or deleting employee records (no update/delete UI or API).
- File/photo uploads, e-signatures, or document generation.
- Email notifications or integrations with HRIS/payroll systems.
- Automated test suites, CI configuration, Docker, or deployment config.
- Multi-page navigation, multi-step wizards, or admin dashboards.
- External dependencies of any kind (frameworks, ORMs, CDNs) — Python 3 standard library only.

### OPEN QUESTIONS

NONE — resolved by the PO by mirroring the prior factory attempt's product behavior: submissions persist to a shared SQLite store (not browser localStorage) because the README frames this as organizational data collection; Python 3 stdlib + SQLite on port 8000 keeps the app dependency-free for a small organization; the field set and option lists follow that attempt's conventions; edit/delete/auth are out of scope for v1.

### SPEC IN GIT

- `BRANCH: devin/1791694335-factory-onboarding-form`
- `FILE: docs/specs/onboarding-form.md`
- `COMMIT: https://github.com/byteclub-labs/employee-onboarding-form/commit/67d55a2`

### STATUS

STATUS: COMPLETE
