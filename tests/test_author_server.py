import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from wsgiref.util import setup_testing_defaults

from author import server


def request(method, path, data=None, origin=None):
    environ = {}
    setup_testing_defaults(environ)
    environ.update(REQUEST_METHOD=method, PATH_INFO=path, HTTP_HOST="localhost:8765")
    body = json.dumps(data).encode() if data is not None else b""
    environ["CONTENT_LENGTH"] = str(len(body))
    environ["wsgi.input"] = io.BytesIO(body)
    if origin is not None:
        environ["HTTP_ORIGIN"] = origin
    response = {}
    def start_response(status, headers):
        response.update(status=status, headers=dict(headers))
    response["body"] = b"".join(server.application(environ, start_response))
    return response


class AuthorServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        root = Path(self.directory.name)
        docs = root / "docs"
        docs.mkdir()
        (docs / "index.md").write_text("# Example\n")
        (root / "topics.json").write_text('[{"id":"algebra","label":"Algebra"}]')
        (root / "mkdocs.yml").write_text("nav:\n  - Home: index.md\n")
        self.root, self.docs = root, docs
        for name, value in (("ROOT", root), ("DOCS", docs), ("TOPICS", root / "topics.json")):
            change = patch.object(server, name, value)
            change.start()
            self.addCleanup(change.stop)

    def test_project_and_page_routes(self):
        project = request("GET", "/api/project")
        self.assertEqual(project["status"], "200 OK")
        self.assertEqual(json.loads(project["body"])["pages"], ["index.md"])
        page = request("GET", "/api/page/index.md")
        self.assertEqual(json.loads(page["body"])["content"], "# Example\n")
        self.assertEqual(request("GET", "/api/page/../topics.json")["status"], "400 Bad Request")

    def test_missing_topics_requires_setup_and_can_be_initialized(self):
        (self.root / "topics.json").unlink()
        project = json.loads(request("GET", "/api/project")["body"])
        self.assertTrue(project["needs_topic_setup"])
        topics = [{"id": "topology", "label": "Topology"}]
        response = request("POST", "/api/topics/initialize", {"topics": topics})
        self.assertEqual(response["status"], "200 OK")
        project = json.loads(request("GET", "/api/project")["body"])
        self.assertFalse(project["needs_topic_setup"])
        self.assertEqual(project["topics"], topics)

    def test_initialization_rejects_invalid_and_existing_catalog(self):
        old = (self.root / "topics.json").read_text()
        response = request("POST", "/api/topics/initialize", {"topics": []})
        self.assertEqual(response["status"], "400 Bad Request")
        self.assertEqual((self.root / "topics.json").read_text(), old)
        (self.root / "topics.json").unlink()
        invalid = [{"id": "Bad ID", "label": "Bad"}]
        response = request("POST", "/api/topics/initialize", {"topics": invalid})
        self.assertEqual(response["status"], "400 Bad Request")
        self.assertFalse((self.root / "topics.json").exists())

    def test_empty_initial_topic_catalog_is_allowed(self):
        (self.root / "topics.json").unlink()
        response = request("POST", "/api/topics/initialize", {"topics": []})
        self.assertEqual(response["status"], "200 OK")
        self.assertEqual(json.loads((self.root / "topics.json").read_text()), [])

    def test_adding_topic_saves_it_immediately(self):
        topic = {"id": "topology", "label": "Topology"}
        response = request("POST", "/api/topics/add", {"topic": topic})
        self.assertEqual(response["status"], "200 OK")
        self.assertIn(topic, json.loads((self.root / "topics.json").read_text()))
        self.assertEqual(request("POST", "/api/topics/add", {"topic": topic})["status"], "400 Bad Request")

    def test_adding_topic_creates_missing_catalog_during_setup(self):
        (self.root / "topics.json").unlink()
        topic = {"id": "topology", "label": "Topology"}
        response = request("POST", "/api/topics/add", {"topic": topic})
        self.assertEqual(response["status"], "200 OK")
        self.assertEqual(json.loads((self.root / "topics.json").read_text()), [topic])
        request("POST", "/api/topics/remove", {"topic": topic})
        self.assertEqual(json.loads((self.root / "topics.json").read_text()), [])

    @patch.object(server, "prepare_preview", return_value="/preview/")
    def test_preview_and_save_routes(self, build):
        payload = {"page": "new-page.md", "content": "# New\n", "topics": [{"id": "algebra", "label": "Algebra"}]}
        preview = request("POST", "/api/preview", payload)
        self.assertEqual(json.loads(preview["body"]), {"url": "/preview/"})
        self.assertFalse((self.docs / "new-page.md").exists())
        saved = request("POST", "/api/save", payload)
        self.assertEqual(json.loads(saved["body"]), {"ok": True})
        self.assertEqual((self.docs / "new-page.md").read_text(), "# New\n")
        self.assertIn("new-page.md", (self.root / "mkdocs.yml").read_text())
        self.assertEqual(build.call_count, 2)

    @patch.object(server, "prepare_preview", side_effect=ValueError("Invalid proof"))
    def test_failed_build_does_not_save(self, _build):
        payload = {"page": "index.md", "content": "bad", "topics": []}
        result = request("POST", "/api/save", payload)
        self.assertEqual(result["status"], "400 Bad Request")
        self.assertEqual(json.loads(result["body"])["error"], "Invalid proof")
        self.assertEqual((self.docs / "index.md").read_text(), "# Example\n")

    def test_foreign_origin_is_rejected(self):
        result = request("POST", "/api/preview", {}, origin="https://elsewhere.example")
        self.assertEqual(result["status"], "400 Bad Request")


if __name__ == "__main__":
    unittest.main()
