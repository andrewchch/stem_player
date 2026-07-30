from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
STEMS_DIR = Path(os.environ.get("STEMS_DIR", BASE_DIR / "stems"))
ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg", "m4a", "flac", "aac"}

app = Flask(__name__)


def _is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _ensure_stems_dir() -> None:
    STEMS_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def index():
    _ensure_stems_dir()
    return render_template("index.html")


@app.get("/api/stems")
def list_stems():
    _ensure_stems_dir()
    stems = []
    for file_path in sorted(STEMS_DIR.iterdir()):
        if file_path.is_file() and _is_allowed_file(file_path.name):
            stems.append({"name": file_path.name, "url": f"/stems/{file_path.name}"})
    return jsonify(stems)


@app.post("/api/upload")
def upload_stems():
    _ensure_stems_dir()
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files provided"}), 400

    uploaded = []
    for file in files:
        filename = secure_filename(file.filename or "")
        if not filename:
            continue
        if not _is_allowed_file(filename):
            continue
        save_path = STEMS_DIR / filename
        file.save(save_path)
        uploaded.append(filename)

    if not uploaded:
        return jsonify({"error": "No valid audio files uploaded"}), 400

    return jsonify({"uploaded": uploaded})


@app.get("/stems/<path:filename>")
def serve_stem(filename: str):
    _ensure_stems_dir()
    return send_from_directory(STEMS_DIR, filename, as_attachment=False)


if __name__ == "__main__":
    _ensure_stems_dir()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
