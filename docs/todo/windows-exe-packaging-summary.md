# Windows EXE Packaging Summary

## Current Project Shape

Fishpool is currently a local web application:

- Backend: Django 5 + Django REST Framework
- Frontend: Vue 3 + Vite + Element Plus
- Database: SQLite at `backend/db.sqlite3`
- Current launcher: `start-dev.bat` starts Django and Vite in two separate development windows

Because this is not a single script, packaging it as a Windows executable means bundling the backend, built frontend assets, database handling, templates, and an application launcher together.

## Recommended Target

Build a `Fishpool.exe` desktop launcher that:

1. Starts a local Django HTTP service, for example `http://127.0.0.1:8000`.
2. Serves the production-built frontend instead of running Vite dev server.
3. Opens the app in the default browser, or optionally in an embedded desktop window.
4. Stores writable data such as SQLite database files under a user-writable directory, for example `%APPDATA%\Fishpool`.
5. Includes import templates such as `docs/templates/customer_import_template.xlsx`.
6. Runs database migrations during first launch or through a controlled initialization step.

## Required Changes

### Frontend

- Run `npm run build` to generate static production assets.
- Configure the frontend API base path so production requests target the bundled backend correctly.
- Copy or reference the built assets from Django static/template serving.

### Backend

- Add a production-friendly local server dependency, such as `waitress`.
- Avoid using `manage.py runserver` as the packaged runtime.
- Set production-oriented settings for packaged use:
  - `DEBUG = False`
  - appropriate `ALLOWED_HOSTS`
  - stable static file handling
- Move the SQLite database path out of the application install/extraction directory and into a writable user data directory.
- Make packaged resource paths work both in source mode and PyInstaller mode.

### Packaging

- Use PyInstaller to package the Python launcher/backend.
- Include:
  - Django project files
  - built frontend static assets
  - Excel import templates
  - migrations
  - any required static files
- Add a launcher script that:
  - prepares the user data directory
  - initializes or migrates the database
  - starts the local HTTP server
  - opens the application URL

## User Experience Goal

The final user flow should be:

```text
Double-click Fishpool.exe
```

Then the application opens automatically at:

```text
http://127.0.0.1:8000
```

or inside an embedded desktop window if a desktop shell is added.

## Important Product Decision

This EXE approach is suitable for single-user local use.

For multi-user usage with shared data, a LAN or server deployment is a better architecture. If every user runs their own EXE with local SQLite, each user will have a separate database unless additional synchronization or a shared database is introduced.

