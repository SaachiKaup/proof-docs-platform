from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup
from mkdocs.exceptions import PluginError
import markdown

ROOT = Path(__file__).parents[1]
spec = spec_from_file_location("topic_checker", ROOT / "plugins/topic_checker.py")
plugin = module_from_spec(spec)
spec.loader.exec_module(plugin)
reference_spec = spec_from_file_location("proof_references", ROOT / "plugins/proof_references.py")
references = module_from_spec(reference_spec)
reference_spec.loader.exec_module(references)
PAGE = SimpleNamespace(file=SimpleNamespace(src_uri="sample.md"))


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "topics.json").write_text(json.dumps([
            {"id": "algebra", "label": "Algebra"},
            {"id": "number-theory", "label": "Number theory"},
        ]))
        change = patch.object(plugin, "ROOT", root)
        change.start()
        self.addCleanup(change.stop)

    def test_multi_topic_block_has_metadata_and_visible_contents(self):
        text = '::: knowledge tags="algebra,number-theory"\nExample $x^2$.\n:::\n'
        result = plugin.on_page_markdown(text, page=PAGE, config={}, files=[])
        self.assertIn('data-knowledge-tags="algebra,number-theory"', result)
        self.assertIn('class="knowledge-content"', result)
        self.assertIn('class="knowledge-reveal" type="button" hidden', result)
        self.assertIn('Example', result)
        self.assertIn('hidden', result)
        rendered = BeautifulSoup(markdown.markdown(result, extensions=["md_in_html"]), "html.parser")
        block = rendered.select_one(".knowledge-block")
        self.assertIsNotNone(block.select_one(".knowledge-reveal[hidden]"))
        self.assertIn("Example", block.select_one(".knowledge-content").get_text())

    def test_unknown_and_malformed_tags_fail_build(self):
        for tags in ['algebra,unknown', 'algebra,', 'Algebra']:
            with self.subTest(tags=tags), self.assertRaises(PluginError):
                plugin.on_page_markdown(f'::: knowledge tags="{tags}"\nText.\n:::\n', page=PAGE, config={}, files=[])

    def test_nested_knowledge_inside_reference_is_processed(self):
        text = '::: proof-ref id="lemma"\n## Lemma\n\n::: knowledge tags="algebra"\nExtra.\n:::\n\n:::\n'
        result = plugin.on_page_markdown(text, page=PAGE, config={}, files=[])
        result = references.on_page_markdown(result, page=PAGE, config={}, files=[])
        self.assertIn('class="reference-source"', result)
        self.assertIn('class="knowledge-block"', result)
        self.assertNotIn('::: knowledge', result)

    def test_selector_is_not_dependent_on_javascript_for_content(self):
        html = '<article class="md-content__inner"><section class="knowledge-block">Extra</section></article>'
        result = plugin.on_post_page(html, page=PAGE, config={})
        self.assertIn('data-knowledge-topic="algebra"', result)
        self.assertIn('class="knowledge-block">Extra', result)

if __name__ == "__main__":
    unittest.main()
