from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import unittest
from mkdocs.exceptions import PluginError

ROOT = Path(__file__).parents[1]
spec = spec_from_file_location("proof_references_knowledge", ROOT / "plugins/proof_references.py")
plugin = module_from_spec(spec)
spec.loader.exec_module(plugin)
PAGE = SimpleNamespace(file=SimpleNamespace(src_uri="sample.md"))


class KnowledgeTests(unittest.TestCase):
    def test_multi_topic_block_has_metadata_and_visible_contents(self):
        text = '::: knowledge tags="algebra,number-theory"\nExample $x^2$.\n:::\n'
        result = plugin.on_page_markdown(text, page=PAGE, config={}, files=[])
        self.assertIn('data-knowledge-tags="algebra,number-theory"', result)
        self.assertIn('Example', result)
        self.assertNotIn('hidden', result)

    def test_unknown_and_malformed_tags_fail_build(self):
        for tags in ['algebra,unknown', 'algebra,', 'Algebra']:
            with self.subTest(tags=tags), self.assertRaises(PluginError):
                plugin.on_page_markdown(f'::: knowledge tags="{tags}"\nText.\n:::\n', page=PAGE, config={}, files=[])

    def test_nested_knowledge_inside_reference_is_processed(self):
        text = '::: proof-ref id="lemma"\n## Lemma\n\n::: knowledge tags="algebra"\nExtra.\n:::\n\n:::\n'
        result = plugin.on_page_markdown(text, page=PAGE, config={}, files=[])
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
