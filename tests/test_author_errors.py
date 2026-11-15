import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("author_server", Path(__file__).parents[1] / "author" / "server.py")
author_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(author_server)


class BuildErrorTests(unittest.TestCase):
    def test_only_relevant_diagnostics_are_shown(self):
        output = """\x1b[31m MkDocs 2.0 warning banner\x1b[0m
INFO    -  Cleaning site directory
ERROR   -  Error reading page 'chapters/proof.md':
ERROR   -  chapters/proof.md: reference 'missing' has no proof-ref block on this page
"""
        result = author_server.relevant_build_errors(output, "")
        self.assertIn("reference 'missing'", result)
        self.assertIn("chapters/proof.md", result)
        self.assertNotIn("MkDocs 2.0", result)
        self.assertNotIn("Cleaning site", result)

    def test_strict_build_warnings_are_kept(self):
        self.assertEqual(author_server.relevant_build_errors("WARNING - Missing page\n", ""), "Missing page")

    def test_unstructured_errors_are_not_lost(self):
        self.assertIn("Traceback", author_server.relevant_build_errors("Traceback: unexpected error", ""))


if __name__ == "__main__":
    unittest.main()
