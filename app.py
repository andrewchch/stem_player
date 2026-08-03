from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
STEMS_DIR = Path(os.environ.get("STEMS_DIR", "/data/stems"))
ALLOWED_EXTENSIONS = {"mp3", "wav", "ogg", "m4a", "flac", "aac"}

app = Flask(__name__)


def _is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _ensure_stems_dir() -> None:
    STEMS_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_folder(folder: str) -> Path | None:
    """Return the resolved path for *folder* under STEMS_DIR, or None if invalid."""
    safe = secure_filename(folder)
    if not safe:
        return None
    resolved = (STEMS_DIR / safe).resolve()
    # Guard against path-traversal
    try:
        resolved.relative_to(STEMS_DIR.resolve())
    except ValueError:
        return None
    return resolved


@app.get("/")
def index():
    _ensure_stems_dir()
    return render_template("index.html")


@app.get("/admin")
def admin():
    _ensure_stems_dir()
    return render_template("admin.html")


@app.get("/api/folders")
def list_folders():
    _ensure_stems_dir()
    folders = sorted(
        p.name for p in STEMS_DIR.iterdir() if p.is_dir()
    )
    return jsonify(folders)


@app.post("/api/folders")
def create_folder():
    _ensure_stems_dir()
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    folder_path = _resolve_folder(name)
    if folder_path is None:
        return jsonify({"error": "Invalid folder name"}), 400
    folder_path.mkdir(exist_ok=True)
    return jsonify({"name": folder_path.name})


@app.get("/api/stems")
def list_stems():
    _ensure_stems_dir()
    folder_name = request.args.get("folder", "")
    if folder_name:
        folder_path = _resolve_folder(folder_name)
        if folder_path is None or not folder_path.is_dir():
            return jsonify({"error": "Folder not found"}), 404
        search_dir = folder_path
        url_prefix = f"/stems/{folder_path.name}/"
    else:
        search_dir = STEMS_DIR
        url_prefix = "/stems/"

    stems = []
    for file_path in sorted(search_dir.iterdir()):
        if file_path.is_file() and _is_allowed_file(file_path.name):
            stat = file_path.stat()
            stems.append({
                "name": file_path.name,
                "url": f"{url_prefix}{file_path.name}",
                "size": stat.st_size,
                "added": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })
    return jsonify(stems)


@app.post("/api/upload")
def upload_stems():
    _ensure_stems_dir()
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files provided"}), 400

    folder_name = request.form.get("folder", "")
    if folder_name:
        folder_path = _resolve_folder(folder_name)
        if folder_path is None or not folder_path.is_dir():
            return jsonify({"error": "Folder not found"}), 404
        save_dir = folder_path
    else:
        save_dir = STEMS_DIR

    uploaded = []
    for file in files:
        filename = secure_filename(file.filename or "")
        if not filename:
            continue
        if not _is_allowed_file(filename):
            continue
        save_path = save_dir / filename
        file.save(save_path)
        uploaded.append(filename)

    if not uploaded:
        return jsonify({"error": "No valid audio files uploaded"}), 400

    return jsonify({"uploaded": uploaded})


@app.delete("/api/stems/<folder>/<filename>")
def delete_stem(folder: str, filename: str):
    _ensure_stems_dir()
    folder_path = _resolve_folder(folder)
    if folder_path is None or not folder_path.is_dir():
        return jsonify({"error": "Folder not found"}), 404

    safe_filename = secure_filename(filename)
    if not safe_filename or not _is_allowed_file(safe_filename):
        return jsonify({"error": "Invalid filename"}), 400

    file_path = folder_path / safe_filename
    # Guard against path-traversal
    try:
        file_path.resolve().relative_to(folder_path.resolve())
    except ValueError:
        return jsonify({"error": "Invalid filename"}), 400

    if not file_path.is_file():
        return jsonify({"error": "File not found"}), 404

    file_path.unlink()
    return jsonify({"deleted": safe_filename})


@app.get("/stems/<path:filename>")
def serve_stem(filename: str):
    _ensure_stems_dir()
    return send_from_directory(STEMS_DIR, filename, as_attachment=False)


@app.get("/images/<path:filename>")
def serve_image(filename: str):
    return send_from_directory(BASE_DIR / "images", filename, as_attachment=False)


if __name__ == "__main__":
    _ensure_stems_dir()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
