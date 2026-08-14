# Fishpool Windows Installer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a per-user Windows installer that keeps an empty-on-first-run SQLite database in a selectable data directory across upgrades and optional uninstall retention.

**Architecture:** Vue is built into Django static resources and Django serves the SPA. A PyInstaller launcher runs migrations, starts Waitress on localhost, and opens the default browser. Inno Setup stores the selected data directory under the current user's registry and asks whether to delete it during uninstall.

**Tech Stack:** Vue/Vite, Django, Waitress, PyInstaller, Inno Setup.

## Global Constraints

- Bind the packaged server only to `127.0.0.1`.
- First use creates an empty database through Django migrations.
- Upgrades and data-retaining uninstalls must reuse the existing database.
- The installer must allow the user to choose the data directory.

### Task 1: Serve the Production SPA

**Files:** `frontend/vite.config.js`, `backend/fishpool/settings.py`, `backend/fishpool/urls.py`

- [ ] Build Vue assets below Django static resources at `/static/frontend/`.
- [ ] Add a catch-all frontend route after all API routes and a health endpoint for the launcher.
- [ ] Enable WhiteNoise static serving for packaged runtime only.

### Task 2: Add Packaged Runtime Support

**Files:** `backend/fishpool/runtime.py`, `backend/fishpool/launcher.py`, `backend/requirements.txt`, `backend/requirements-packaging.txt`, `backend/customers/views.py`

- [ ] Resolve the data directory from `HKCU\Software\Fishpool\DataDirectory`, falling back to `%LOCALAPPDATA%\Fishpool`.
- [ ] Run migrations before Waitress binds a localhost port, then open the browser after `/health/` responds.
- [ ] Resolve Excel templates from the PyInstaller resource directory.

### Task 3: Build and Install

**Files:** `packaging/build-installer.ps1`, `packaging/Fishpool.iss`, `.gitignore`

- [ ] Build frontend assets, package the launcher with PyInstaller, and compile an Inno Setup installer.
- [ ] Store the selected data directory in the current-user registry without deleting it on normal uninstall.
- [ ] Offer an uninstall checkbox to delete the data directory and registry setting permanently.

### Task 4: Verify

**Files:** `backend/customers/tests.py`

- [ ] Run Django tests and Vite production build.
- [ ] Run the packaging script after PyInstaller and Inno Setup are installed, then test first install, upgrade, retain-data uninstall, and delete-data uninstall.
