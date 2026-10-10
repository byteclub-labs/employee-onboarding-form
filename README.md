# employee-onboarding-form
Single-page HTML data collection form for new employee joining (small organization)

## Run locally

Requires Python 3 (standard library only — nothing to install):

```
python3 server.py
```

Then open http://localhost:8000. Set `PORT` to change the port.

Submissions persist in `data/onboarding.db` (SQLite, auto-created on first run and gitignored).

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/employees` | `{count, employees[]}` newest first |
| POST | `/api/employees` | Onboard an employee `{full_name, email, phone, job_title, department, employment_type, start_date, address?, emergency_contact_name?, emergency_contact_phone?, notes?}` |
