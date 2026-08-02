# Stem Player

A browser-based web app for uploading, managing, and playing back audio stem files. Upload individual tracks (drums, bass, vocals, etc.) and play them back in perfect sync, with per-stem volume, mute, and solo controls.

## Features

- **Upload audio stems** – supports MP3, WAV, OGG, M4A, FLAC, and AAC files (multiple files at once).
- **Synchronized playback** – Play, Pause, and Stop all stems simultaneously, keeping them in sync.
- **Per-stem mixing** – Adjust the volume, mute, or solo any individual stem.
- **Solo mode** – When any stem is soloed, all other stems are automatically muted.
- **Persistent storage** – Uploaded stems are saved on disk and reloaded automatically on the next visit.

## Architecture

The app is a lightweight [Flask](https://flask.palletsprojects.com/) backend with a single-page vanilla-JavaScript frontend.

| Component | Details |
|-----------|---------|
| `app.py` | Flask application – serves the UI and exposes the REST API |
| `templates/index.html` | Single-page frontend (HTML + CSS + JS, no build step) |
| `stems/` | Directory where uploaded audio files are stored (created automatically) |

### REST API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the main UI |
| `GET` | `/api/stems` | Returns a JSON list of all uploaded stems |
| `POST` | `/api/upload` | Accepts one or more audio files (`multipart/form-data`, field name `files`) |
| `GET` | `/stems/<filename>` | Streams a stem file for playback |

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STEMS_DIR` | `<app dir>/stems` | Directory where stem files are stored |
| `PORT` | `5000` | Port the server listens on |

## Setup & Run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

## Test

```bash
python -m unittest -q
```

Tests are in `test_app.py` and use Python's built-in `unittest` module with Flask's test client. Each test runs against a temporary directory so no real files are written to disk.
