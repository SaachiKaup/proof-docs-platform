from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import markdown


ROOT = Path(__file__).parents[1]
PAGE = SimpleNamespace(file=SimpleNamespace(src_uri="chapters/topological-extensions.md"))


def load_hook(name):
    spec = spec_from_file_location(name, ROOT / "plugins" / f"{name}.py")
    hook = module_from_spec(spec)
    spec.loader.exec_module(hook)
    return hook


class ImportedProofTests(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / "docs/chapters/topological-extensions.md").read_text()

    def test_preserves_reviewed_mathematical_details(self):
        self.assertIn("$H_0$ constant and $H_1=L\\cdot R^{-1}$", self.text)
        self.assertIn("the image of $A\\inc EA\\to \\tilde G$", self.text)
        self.assertIn(r'\arrow[r, "\Pi", dashed]', self.text)
        self.assertIn(r'\arrow[rr, "\alpha(\calE)", bend left]', self.text)
        self.assertIn("which way", self.text)
        self.assertEqual(self.text.count('<script type="text/tikz">'), 5)

    def test_topic_and_reference_wrappers_work_together(self):
        knowledge = load_hook("topic_checker")
        references = load_hook("proof_references")
        with patch.object(knowledge, "load_topics", return_value=[{"id": "group-cohomology", "label": "Group cohomology"}]):
            result = knowledge.on_page_markdown(self.text, page=PAGE, config={}, files=[])
        result = references.on_page_markdown(result, page=PAGE, config={}, files=[])
        self.assertIn('data-knowledge-tags="group-cohomology"', result)
        for identifier in ("homotopy-orbits", "lift-lemma", "cocycle-formula"):
            self.assertIn(f'data-reference-id="{identifier}"', result)

    def test_surjectivity_heading_has_clean_navigation_label(self):
        heading = next(line for line in self.text.splitlines() if line.startswith("## 4. Essential surjectivity"))
        renderer = markdown.Markdown(extensions=["toc", "markdown_katex"])
        renderer.convert(heading)
        self.assertEqual(renderer.toc_tokens[0]["name"], "4. Essential surjectivity of α")


if __name__ == "__main__":
    unittest.main()
