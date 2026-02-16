# GitHub Copilot instructions — apartment-reservation-manager

Purpose: give AI coding agents the minimal, precise knowledge needed to be productive in this repo.

## Big picture
- Single-process Flask app implemented in `app.py` (no separate service layers). UI + server + DB logic all live in `app.py`.
- SQLite (file `reservations.db`) is the persistent store via `Flask-SQLAlchemy`.
- Frontend: Jinja templates in `templates/` and CSS in `static/css/style.css`.
- Deployment: `Procfile` → `gunicorn app:app` (Heroku/Gunicorn style).

## Source-of-truth and where to change things
- Treat `app.py` as authoritative (routes, session flags, auth). Backup/TUTORIAL/README sometimes show older behaviour.
- Key files to inspect before edits: `app.py`, `templates/index.html`, `templates/add_reservation.html`, `templates/edit_reservation.html`, `templates/calendar.html`, `templates/login_select.html`, `static/css/style.css`.

## Important runtime details / commands
- Dev run: `pip install -r requirements.txt` then `python app.py` (DB auto-created via `db.create_all()`).
- Prod run: `gunicorn app:app` (Procfile provided).
- Environment vars used: `SECRET_KEY`, `ADMIN_PASSWORD`, `PORT`.
- DB file location: `./reservations.db` (no migrations configured).

## Auth & access patterns (critical)
- Session flags control access:
  - `session['admin_logged_in']` → admin (full access)
  - `session['readonly_mode']` → view-only (blocks create/update/delete)
- Routes that flip flags: `/admin-login` (POST), `/admin-logout`, `/readonly` (sets read-only without password), `/exit-readonly`.
- Route-level protection:
  - `@require_admin` — use on routes that modify data (add/edit/delete).
  - `@check_readonly` — prevents modifications while `readonly_mode` is set.
  - Example: `@require_admin` + `@check_readonly` on `add_reservation` in `app.py`.

## API & data model
- Model: `Reservation` (defined in `app.py`) — columns: `guest_name`, `platform`, `check_in`, `check_out`, `adults`, `children`, `special_requests`, `notes`, `created_at`.
- JSON API endpoint: `GET /api/reservations` returns `[Reservation.to_dict(), ...]`.
- Date validation: code enforces `check_out > check_in` in add/edit handlers — replicate this check for any new date logic.

## Project-specific conventions & gotchas
- Single-file Flask app — prefer minimal, local edits to `app.py` and templates.
- No DB migrations. When adding/removing model fields: update `Reservation`, update templates and `to_dict()`, then recreate `reservations.db` (or add Flask-Migrate before making schema changes).
- Documentation mismatch: `TUTORIAL.md`, `README.md`, and `templates/readonly_login.html` describe a password-protected read-only login (READONLY_PASSWORD). Current `app.py` does NOT use a readonly password — it uses `/readonly` (no password). Use `app.py` as source-of-truth and update docs/templates if you change behaviour.
- Hard-coded defaults exist (e.g. `ADMIN_PASSWORD` default in `app.py`) — consider moving secrets to env vars.

## When you add features
1. Update `Reservation` model (in `app.py`).
2. Update `templates/add_reservation.html` and `templates/edit_reservation.html` (form field names must match model attributes).
3. Add the new key to `Reservation.to_dict()` if it should appear in the JSON API.
4. Handle DB migration (manual delete/recreate or add Flask‑Migrate).

## Debugging & manual checks
- Inspect DB with `sqlite3 reservations.db` or a DB browser.
- Look for session values in templates: `is_readonly` and `is_admin` are passed by `index()` and `calendar_view()`.
- Flash messages are used for user-visible errors — check templates for `get_flashed_messages()`.

## Quick examples (copy/paste)
- Run dev server: `pip install -r requirements.txt && python app.py`
- Start production server: `gunicorn app:app`
- Reset DB: `rm reservations.db && python app.py` (will recreate schema)
- Add `@require_admin` to a route to restrict it to admins (see `add_reservation`)

## Recommended first PRs for contributors
- Sync docs/templates with the current `app.py` behavior (remove/restore passworded readonly flow consistently).
- Add a lightweight test that exercises add/edit/delete via Flask test client.
- Add basic DB migration tooling (`Flask-Migrate`) or a short migration guide in README.

---
Notes / source-of-truth: prefer `app.py` over `TUTORIAL.md`/`README.md`/`templates/readonly_login.html` when they conflict. If you'd like, I can: update docs to match code, reinstate passworded readonly flow, or add migrations/tests — tell me which to do next.
