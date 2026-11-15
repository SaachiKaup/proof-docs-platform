from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import json
import unittest

from mkdocs.exceptions import PluginError
from bs4 import BeautifulSoup
import markdown
import yaml


ROOT = Path(__file__).parents[1]
CHAPTER = (ROOT / "docs/chapters/01-even-numbers.md").read_text()
SCRIPT = (ROOT / "docs/javascripts/reference-panel.js").read_text()
CONFIG = (ROOT / "mkdocs.yml").read_text()
PLUGIN_PATH = ROOT / "plugins/proof_references.py"
SPEC = spec_from_file_location("proof_references", PLUGIN_PATH)
proof_references = module_from_spec(SPEC)
SPEC.loader.exec_module(proof_references)
PAGE = SimpleNamespace(file=SimpleNamespace(src_uri="sample.md"))


class ProofReferenceTests(unittest.TestCase):
    def test_sample_uses_directives_not_author_html(self):
        self.assertIn('::: proof-ref id="definition-even"', CHAPTER)
        self.assertIn('[[Lemma 1.2|lemma-even-square]]', CHAPTER)
        self.assertNotIn('<section', CHAPTER)
        self.assertNotIn('<button', CHAPTER)

    def test_python_hook_generates_sections_and_buttons(self):
        rendered = proof_references.on_page_markdown(CHAPTER, page=PAGE, config={}, files=[])
        self.assertIn('class="reference-source"', rendered)
        self.assertIn('class="reference-trigger"', rendered)
        self.assertIn('data-reference-id="lemma-even-square"', rendered)

    def test_missing_reference_is_a_build_error(self):
        with self.assertRaises(PluginError):
            proof_references.on_page_markdown('[[Missing lemma|not-defined]]', page=PAGE, config={}, files=[])

    def test_latex_references_follow_shared_theorem_numbering(self):
        text = '''## 2. Background

::: proof-ref id="first" type="theorem"
\\label{first theorem}
First statement.
:::

::: proof-ref id="second" type="lemma"
\\label{second_lemma}
Second statement.
:::

By \\Cref{second_lemma} and \\cref{first theorem}.
'''
        rendered = proof_references.on_page_markdown(text, page=PAGE, config={}, files=[])
        self.assertIn('### Lemma 2.2', rendered)
        self.assertIn('data-reference-id="second" aria-label="Lemma 2.2">2.2</button>', rendered)
        self.assertIn('data-reference-id="first" aria-label="theorem 2.1">2.1</button>', rendered)
        earlier = '::: proof-ref id="new" type="proposition"\n\\label{new}\nNew statement.\n:::\n\n'
        changed = proof_references.on_page_markdown(text.replace('::: proof-ref id="second"', earlier + '::: proof-ref id="second"'), page=PAGE, config={}, files=[])
        self.assertIn('### Lemma 2.3', changed)
        self.assertIn('data-reference-id="second" aria-label="Lemma 2.3">2.3</button>', changed)

    def test_missing_latex_reference_is_a_build_error(self):
        with self.assertRaises(PluginError):
            proof_references.on_page_markdown(r'By \Cref{missing}.', page=PAGE, config={}, files=[])

    def test_forward_references_and_section_counter_reset(self):
        text = '''## 1. First

See \\Cref{later label} twice: \\cref{later label}.

::: proof-ref id="first" type="theorem"
\\label{first}
First statement.
:::

## 2. Second

::: proof-ref id="later" type="lemma"
\\label{later label}
Second statement.
:::
'''
        result = proof_references.on_page_markdown(text, page=PAGE, config={}, files=[])
        self.assertIn('### Theorem 1.1', result)
        self.assertIn('### Lemma 2.1', result)
        self.assertIn('data-reference-id="later" aria-label="Lemma 2.1">2.1</button>', result)
        self.assertIn('data-reference-id="later" aria-label="lemma 2.1">2.1</button>', result)
        self.assertNotIn(r'\label{later label}', result)

    def test_invalid_latex_reference_targets_are_reported(self):
        cases = {
            'no label': '## 1. Section\n\n::: proof-ref id="first" type="lemma"\nNo label.\n:::\n',
            'duplicate labels': '## 1. Section\n\n::: proof-ref id="first" type="lemma"\n\\label{same}\nFirst.\n:::\n\n::: proof-ref id="second" type="theorem"\n\\label{same}\nSecond.\n:::\n',
            'no numbered section': '::: proof-ref id="first" type="lemma"\n\\label{first}\nStatement.\n:::\n',
            'multiple labels in reference': r'\Cref{first,second}',
        }
        for name, text in cases.items():
            with self.subTest(name=name), self.assertRaises(PluginError):
                proof_references.on_page_markdown(text, page=PAGE, config={}, files=[])

    def test_latex_reference_opens_card_with_the_matching_statement(self):
        text = '''## 1. Background

::: proof-ref id="important-lemma" type="lemma"
\\label{lemma key}
The original mathematical statement.
:::

See \\Cref{lemma key}.
'''
        prepared = proof_references.on_page_markdown(text, page=PAGE, config={}, files=[])
        content = markdown.markdown(prepared, extensions=['md_in_html'])
        page = '<article class="md-content__inner">' + content + '</article>'
        soup = BeautifulSoup(proof_references.on_post_page(page, page=PAGE, config={}), 'html.parser')
        button = soup.select_one('button.reference-trigger')
        card = soup.select_one('aside.reference-card')
        self.assertEqual(button.get_text(strip=True), '1.1')
        self.assertEqual(button['aria-label'], 'Lemma 1.1')
        self.assertEqual(button['data-reference-id'], card['data-reference-id'])
        self.assertIn('The original mathematical statement.', card.get_text())
        self.assertIsNone(card.select_one('a.reference-card__source'))

    def test_plain_display_math_is_prepared_for_rendering(self):
        text = '$$\nA \\xrightarrow{f} B\n$$'
        result = proof_references.on_page_markdown(text, page=PAGE, config={}, files=[])
        self.assertIn('```math\nA \\xrightarrow{f} B\n```', result)

    def test_static_ui_module_does_not_build_or_clone_proof_content(self):
        self.assertNotIn("cloneNode", SCRIPT)
        self.assertNotIn("renderMath", SCRIPT)
        self.assertNotIn("innerHTML", SCRIPT)
        self.assertNotIn("IntersectionObserver", SCRIPT)
        self.assertNotIn("card.hidden = false;\n    host.append(card)", SCRIPT)
        self.assertIn('document.addEventListener("click"', SCRIPT)
        self.assertNotIn("addEventListener(\"click\", () => open", SCRIPT)
        self.assertIn("closeWhenTriggerLeavesViewport", SCRIPT)

    def test_build_hook_expands_proof_inside_card(self):
        page_html = '''<article class="md-content__inner">
        <section class="reference-source" id="lemma-even-square"><h2 id="lemma">Lemma 1.2</h2><p>Statement.</p><p><strong>Proof.</strong> Proof text.</p></section>
        </article>'''
        rendered = proof_references.on_post_page(page_html, page=PAGE, config={})
        soup = BeautifulSoup(rendered, 'html.parser')
        card = soup.select_one('.reference-card')
        self.assertIn('Statement.', card.select_one('.reference-card__content').get_text())
        self.assertNotIn('Proof text.', card.select_one('.reference-card__content').get_text())
        self.assertIn('Proof text.', card.select_one('details').get_text())
        self.assertEqual(card.select_one('summary').get_text(), 'Open full section')
        self.assertFalse(card.select_one('details').has_attr('open'))
        self.assertIsNone(card.select_one('a[href="#lemma-even-square"]'))

    def test_build_hook_attaches_only_matching_separate_proof(self):
        page_html = '''<article class="md-content__inner">
        <section class="reference-source" id="lemma"><h2>Lemma</h2><p>Statement.</p></section>
        <div class="proof-details" data-reference-id="lemma"><p id="original-proof">The proof.</p></div>
        <div class="proof-details" data-reference-id="other"><p>Unrelated proof.</p></div>
        </article>'''
        soup = BeautifulSoup(proof_references.on_post_page(page_html, page=PAGE, config={}), 'html.parser')
        card = soup.select_one('.reference-card')
        self.assertIn('The proof.', card.select_one('details').get_text())
        self.assertNotIn('Unrelated proof.', card.get_text())
        self.assertIsNone(card.select_one('#original-proof'))
        self.assertIsNotNone(soup.select_one('#original-proof'))

    def test_static_katex_and_left_toc_are_configured(self):
        self.assertIn("markdown_katex", CONFIG)
        self.assertIn("toc.integrate", CONFIG)
        self.assertNotIn("katex.min.js", CONFIG)

    def test_katex_stylesheet_matches_renderer_version(self):
        config = yaml.safe_load(CONFIG)
        package = json.loads((ROOT / "package.json").read_text())
        version = package["devDependencies"]["katex"]
        self.assertIn(f"https://cdn.jsdelivr.net/npm/katex@{version}/dist/katex.min.css", config["extra_css"])
        katex = next(item["markdown_katex"] for item in config["markdown_extensions"]
                     if isinstance(item, dict) and "markdown_katex" in item)
        self.assertFalse(katex["insert_fonts_css"])

    def test_tikzjax_uses_matched_fork_assets_without_symbol_patches(self):
        config = yaml.safe_load(CONFIG)
        base = 'https://cdn.jsdelivr.net/npm/@rod2ik/tikzjax@1.6.0/dist/'
        self.assertIn(base + 'fonts.min.css', config['extra_css'])
        self.assertIn(base + 'tikzjax.min.js', config['extra_javascript'])
        self.assertNotIn('javascripts/tikz-slashes.js', config['extra_javascript'])


if __name__ == "__main__":
    unittest.main()
