# Copilot Instructions for Stem Player

## Project Overview

Stem Player is a Flask web application that lets users upload, manage, and play back audio stem files in a browser. Key files:

- `app.py` – Flask backend (REST API and static file serving)
- `templates/index.html` – Single-page frontend (HTML + CSS + vanilla JS, no build step)
- `requirements.txt` – Python dependencies
- `test_app.py` – Python unit tests using `unittest` and Flask's test client

## Coding Guidelines

### General
- Keep changes minimal and focused. Do not refactor unrelated code.
- Prefer clarity and simplicity over cleverness.
- Follow existing code style within each file (indentation, naming, import order).

### Python (`app.py`, `test_app.py`)
- Use Python 3.10+ features where appropriate.
- Follow [PEP 8](https://peps.python.org/pep-0008/) style (4-space indentation, snake_case).
- Type-annotate all new functions and parameters using standard library types (`str`, `list`, `Path`, etc.).
- Use `from __future__ import annotations` when adding new modules.
- Do not introduce new dependencies without updating `requirements.txt` and checking for security advisories.

### Flask API
- Keep endpoints RESTful. Use the correct HTTP methods (`GET`, `POST`, etc.).
- Return JSON responses for all `/api/*` routes.
- Return appropriate HTTP status codes (200, 400, 404, etc.).
- Never expose raw filesystem paths or internal tracebacks to the client.

### Frontend (`templates/index.html`)
- Use vanilla JavaScript only – do not introduce frameworks or npm.
- Keep all JavaScript inside the existing `<script>` block.
- Ensure the UI degrades gracefully when no stems are uploaded.

## Testing Requirements

**All changes to `app.py` must be accompanied by Python unit tests in `test_app.py`.**

### Test conventions
- Use Python's built-in `unittest.TestCase`.
- Use Flask's built-in test client (`app.test_client()`).
- Isolate tests from the real filesystem by pointing `stem_app.STEMS_DIR` at a `tempfile.TemporaryDirectory()` in `setUp`, and clean it up in `tearDown`.
- Test both the happy path and error/edge cases (e.g., missing files, unsupported formats, empty requests).
- Name test methods descriptively: `test_<what_is_being_tested>`.

### Running tests
```bash
python -m unittest -q
```

### Example test structure
```python
import io
import tempfile
import unittest
from pathlib import Path

import app as stem_app


class MyFeatureTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        stem_app.STEMS_DIR = Path(self.temp_dir.name)
        self.client = stem_app.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_my_new_endpoint_returns_200(self):
        response = self.client.get("/api/my-endpoint")
        self.assertEqual(response.status_code, 200)
```

## Allowed Audio Formats

The server currently accepts: `mp3`, `wav`, `ogg`, `m4a`, `flac`, `aac`.  
If you add new formats, update `ALLOWED_EXTENSIONS` in `app.py` **and** add a test that uploads a file with the new extension.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STEMS_DIR` | `<app dir>/stems` | Where uploaded audio files are stored |
| `PORT` | `5000` | Port the Flask server listens on |

Do not hard-code these values; always read from the environment with a sensible default.
