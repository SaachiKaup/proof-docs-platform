"""Build an imported document with the same MkDocs hooks as the editor."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

from bs4 import BeautifulSoup
import yaml
from latex_import import convert

ROOT = Path(__file__).resolve().parents[1]


class ImportBuildTests(unittest.TestCase):
    def test_imported_page_builds_with_reference_cards_and_math(self):
        source = r'''\documentclass{article}
\begin{document}
\section{Example}
See \Cref{important}, equation \eqref{identity}, and \cite{source}.
\begin{lemma}\label{important}For each $x$, $x=x$.\end{lemma}
\begin{proof}The identity is immediate.\end{proof}
\begin{knowledge}{algebra}
The distributive law gives $2(a+b)=2a+2b$.
\end{knowledge}
\begin{equation}\label{identity}x=x\end{equation}
\begin{thebibliography}{9}
\bibitem{source} An author. A book. \url{https://example.org/book}.
\end{thebibliography}
\end{document}'''
        content, _ = convert(source)
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / 'docs').mkdir()
            shutil.copytree(ROOT / 'docs/stylesheets', project / 'docs/stylesheets')
            shutil.copytree(ROOT / 'docs/javascripts', project / 'docs/javascripts')
            shutil.copy2(ROOT / 'docs/tex-macros.txt', project / 'docs/tex-macros.txt')
            shutil.copytree(ROOT / 'plugins', project / 'plugins')
            config = yaml.safe_load((ROOT / 'mkdocs.yml').read_text())
            config['nav'] = [{'Imported': 'imported.md'}]
            (project / 'mkdocs.yml').write_text(yaml.safe_dump(config, sort_keys=False))
            (project / 'topics.json').write_text(json.dumps([{"id": "algebra", "label": "Algebra"}]))
            (project / 'node_modules').symlink_to(ROOT / 'node_modules', target_is_directory=True)
            (project / 'docs' / 'imported.md').write_text(content)
            result = subprocess.run([sys.executable, '-m', 'mkdocs', 'build', '--strict'],
                                    cwd=project, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr)
            html = BeautifulSoup((project / 'site/imported/index.html').read_text(), 'html.parser')
            button = html.select_one('button[data-reference-id="important"]')
            self.assertEqual(button.get_text(strip=True), '1.1')
            card = html.select_one('.reference-card[data-reference-id="important"]')
            self.assertIsNotNone(card)
            self.assertIn('The identity is immediate.', card.select_one('details').get_text())
            self.assertEqual(card.select_one('summary').get_text(), 'Open full section')
            self.assertIsNotNone(html.select_one('#eq-identity'))
            self.assertIsNotNone(html.select_one('a[href="#eq-identity"]'))
            self.assertIsNotNone(html.select_one('a[href="#bib-source"]'))
            self.assertIsNotNone(html.select_one('#bib-source'))
            self.assertIsNotNone(html.select_one('a[href="https://example.org/book"]'))
            knowledge = html.select_one('.knowledge-block[data-knowledge-tags="algebra"]')
            self.assertEqual(knowledge.select_one('.knowledge-reveal').get_text(strip=True), 'Show explanation')
            self.assertIn('2(a+b)=2a+2b', knowledge.select_one('.knowledge-content').get_text())
            self.assertIn('An author. A book.', html.get_text())
            self.assertTrue(html.select('.katex'))


if __name__ == '__main__':
    unittest.main()
