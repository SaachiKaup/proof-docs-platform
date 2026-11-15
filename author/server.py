"""Local-only editor for proof-docs. Run with .venv/bin/python author/server.py."""
from __future__ import annotations

from http import HTTPStatus
import json
import mimetypes
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from urllib.parse import unquote
from wsgiref.simple_server import make_server

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TOPICS = ROOT / "topics.json"
TEMP = tempfile.TemporaryDirectory(prefix="proof-docs-editor-")
STAGE = Path(TEMP.name) / "project"
SITE = STAGE / "site"
ID = re.compile(r"[a-z][a-z0-9-]*\Z")
BUILD_LOCK = threading.Lock()
MAX_REQUEST_BYTES = 2_000_000


def relevant_build_errors(stderr, stdout):
    """Keep useful build diagnostics, with a fallback for unstructured errors."""
    output = "\n".join(part for part in (stderr, stdout) if part)
    output = re.sub(r"\x1b\[[0-9;]*m", "", output)
    diagnostics = []
    for line in output.splitlines():
        match = re.match(r"\s*(ERROR|WARNING)\s*-\s*(.*)", line)
        if match:
            message = match.group(2).strip()
            if message and message not in diagnostics:
                diagnostics.append(message)
    return "\n".join(diagnostics) if diagnostics else output.strip() or "The build failed without an error message."


def page_path(name):
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*(?:/[a-z0-9][a-z0-9-]*)*\.md", name):
        raise ValueError("Use a Markdown path with lowercase letters, numbers, hyphens and folders.")
    path = (DOCS / name).resolve()
    if not path.is_relative_to(DOCS.resolve()):
        raise ValueError("Invalid page path")
    return path


def validate_topics(topics):
    if not isinstance(topics, list):
        raise ValueError("Topics must be a list")
    seen = set()
    for topic in topics:
        if not isinstance(topic, dict) or not ID.fullmatch(topic.get("id", "")) or not isinstance(topic.get("label"), str) or not topic["label"].strip() or topic["id"] in seen:
            raise ValueError("Each topic needs a unique lowercase ID and a non-empty label.")
        seen.add(topic["id"])
    return topics


def prepare_preview(page, content, topics):
    page_path(page)
    validate_topics(topics)
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir()
    shutil.copytree(DOCS, STAGE / "docs")
    shutil.copytree(ROOT / "plugins", STAGE / "plugins", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "mkdocs.yml", STAGE / "mkdocs.yml")
    (STAGE / "topics.json").write_text(json.dumps(topics), encoding="utf-8")
    (STAGE / "node_modules").symlink_to(ROOT / "node_modules", target_is_directory=True)
    draft = STAGE / "docs" / page
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(content, encoding="utf-8")
    cfg = yaml.safe_load((STAGE / "mkdocs.yml").read_text())
    if page not in json.dumps(cfg.get("nav", [])):
        cfg.setdefault("nav", []).append({page: page})
        (STAGE / "mkdocs.yml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    result = subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict"], cwd=STAGE, capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise ValueError(relevant_build_errors(result.stderr, result.stdout))
    return "/preview/" if page == "index.md" else "/preview/" + page[:-3] + "/"


def project_data():
    return {
        "topics": json.loads(TOPICS.read_text(encoding="utf-8")),
        "pages": sorted(str(path.relative_to(DOCS)) for path in DOCS.rglob("*.md")),
    }


def save_page(data):
    path = page_path(data["page"])
    topics = validate_topics(data["topics"])
    # Validate the whole draft before writing either the page or the topics.
    prepare_preview(data["page"], data["content"], topics)
    is_new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data["content"], encoding="utf-8")
    TOPICS.write_text(json.dumps(topics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if is_new:
        config_path = ROOT / "mkdocs.yml"
        config = yaml.safe_load(config_path.read_text())
        config.setdefault("nav", []).append({data["page"]: data["page"]})
        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return {"ok": True}


def json_response(value, status=HTTPStatus.OK):
    return status, "application/json; charset=utf-8", json.dumps(value).encode("utf-8")


def static_response(path):
    is_preview = path.startswith("/preview/")
    base = SITE if is_preview else ROOT / "author"
    relative = path.removeprefix("/preview/") if is_preview else path.lstrip("/")
    file = (base / (relative or "index.html")).resolve()
    if file.is_dir():
        file = file / "index.html"
    if not file.is_relative_to(base.resolve()) or not file.is_file():
        return json_response({"error": "Not found"}, HTTPStatus.NOT_FOUND)
    return HTTPStatus.OK, mimetypes.guess_type(file.name)[0] or "application/octet-stream", file.read_bytes()


def read_request_json(environ):
    origin = environ.get("HTTP_ORIGIN")
    if origin not in (None, f"http://{environ.get('HTTP_HOST')}"):
        raise ValueError("Requests must come from the local editor")
    length = int(environ.get("CONTENT_LENGTH") or "0")
    if length < 0 or length > MAX_REQUEST_BYTES:
        raise ValueError("Request too large")
    return json.loads(environ["wsgi.input"].read(length))


def route_request(environ):
    """Return (status, content type, bytes) for one local editor request."""
    method = environ.get("REQUEST_METHOD", "GET")
    path = unquote(environ.get("PATH_INFO", ""))
    if method == "GET":
        if path == "/api/project":
            return json_response(project_data())
        if path.startswith("/api/page/"):
            return json_response({"content": page_path(path.removeprefix("/api/page/")).read_text(encoding="utf-8")})
        return static_response(path)
    if method == "POST" and path in ("/api/preview", "/api/save"):
        data = read_request_json(environ)
        with BUILD_LOCK:
            if path == "/api/preview":
                return json_response({"url": prepare_preview(data["page"], data["content"], data["topics"])})
            return json_response(save_page(data))
    return json_response({"error": "Not found"}, HTTPStatus.NOT_FOUND)


def application(environ, start_response):
    try:
        status, content_type, data = route_request(environ)
    except (KeyError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        status, content_type, data = json_response({"error": str(error)}, HTTPStatus.BAD_REQUEST)
    start_response(f"{status.value} {status.phrase}", [
        ("Content-Type", content_type),
        ("Content-Length", str(len(data))),
        ("Cache-Control", "no-store"),
    ])
    return [data]


def main():
    try:
        with make_server("127.0.0.1", 8765, application) as server:
            print("Proof editor: http://127.0.0.1:8765/", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        TEMP.cleanup()


if __name__ == "__main__":
    main()
