# EBMS (Electricity Bill Management System)

This is a very simple flask app for managing electricity bills. Users here can register,
log in, track their bills, and file complaints. Admins can manage the users
and complaints from a separate panel.

## Tech Stack Used
- Python, Flask
- SQLite for local development, MySQL for production (switches automatically based on `APP_ENV`)
- Passwords hashed with bcrypt
- Rate limiting on login/register/recovery via Flask-Limiter

## Getting Started

```bash
python -m venv venv
venv\Scripts\activate      # on Windows Use this
source venv/bin/activate   # on Mac/Linux use this
pip install -r requirements.txt
copy .env.example .env

python app.py
```

The app runs at `http://localhost:8000` by default. In development mode
it uses a local SQLite file (`database/ebms_dev.db`) so no database setup
is needed to get started.

## Switching to production
Set `APP_ENV=production` in `.env` and fill in the `DB_*` values for a
MySQL database. The app picks the right database automatically, see
`src/data/database.py`.

## Project Layout

```
app.py              entry point, routes for home/features/about/dashboard
src/api/             route blueprints (auth, bills, complaints, admin)
src/services/        business logic, one file per feature
src/models/          database access, one file per table
src/utils/           validators, login/admin guards
src/info/            page copy, security questions, billing config
src/data/            database connection setup
database/            SQL schema files
templates/           HTML pages
static/              CSS, JS, images
```
