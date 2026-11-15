"""Behavioral tests for the LaTeX importer; input files stay untouched."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from latex_import import convert
from latex_import.syntax import group, environment

ROOT = Path(__file__).resolve().parents[1]


def document(body, preamble=""):
    return preamble + "\n\\begin{document}\n" + body + "\n\\end{document}\n"


class ImportTexTests(unittest.TestCase):
    def test_balanced_groups_and_comments_in_environments(self):
        self.assertEqual(group(r"{a {b} \} c}", 0)[0], r"a {b} \} c")
        source = "\\begin{proof}\n% \\end{proof}\nContent.\n\\end{proof}"
        self.assertIn('Content.', environment(source, 0)[1])
        output, _ = convert(document(source))
        self.assertIn('**Proof.** Content.', output)

    def test_statements_forward_references_and_equation_numbers(self):
        source = document(r'''\section{Background}
See \Cref{later}, and \eqref{eq one}.
\begin{lemma}\label{later}
For $x$, we have $x=x$.
\end{lemma}
\begin{equation}\label{eq one}
x=x
\end{equation}''')
        output, diagnostics = convert(source)
        self.assertIn('::: proof-ref id="later" type="lemma"', output)
        self.assertIn(r'\label{later}', output)
        self.assertIn(r'\Cref{later}', output)
        self.assertIn('[(1)](#eq-eq-one)', output)
        self.assertIn(r'x=x\tag{1}', output)
        self.assertTrue(any('numbering assumes' in message for message in diagnostics))

    def test_knowledge_environment_becomes_topic_tagged_markdown(self):
        source = document(r'''\section{One}
\begin{knowledge}{algebra, number-theory}
Optional background: $2(a+b)=2a+2b$.
\end{knowledge}''')
        output, _ = convert(source)
        self.assertIn('::: knowledge tags="algebra,number-theory"', output)
        self.assertIn('Optional background: $2(a+b)=2a+2b$.', output)

    def test_invalid_knowledge_tags_are_preserved_and_reported(self):
        source = document(r'''\section{One}
\begin{knowledge}{Algebra}
Optional background.
\end{knowledge}''')
        output, diagnostics = convert(source)
        self.assertIn(r'\begin{knowledge}{Algebra}', output)
        self.assertTrue(any('knowledge environment needs' in message for message in diagnostics))

    def test_diagram_code_preserved_and_macro_forwarded(self):
        diagram = r'\begin{tikzcd}' + '\n' + r'A/\calE \arrow[r] & B' + '\n' + r'\end{tikzcd}'
        output, warnings = convert(document('$$\n' + diagram + '\n$$', r'\newcommand{\calE}{\mathcal{E}}'))
        self.assertIn(diagram, output)
        self.assertIn(r'\def\calE{\mathcal{E}}', output)
        self.assertIn('data-tex-packages=', output)
        self.assertTrue(any('human-written description' in message for message in warnings))

    def test_footnotes_and_references_inside_them(self):
        source = document(r'''\section{One}
\begin{lemma}\label{a}A statement.\end{lemma}
A note.\footnote{See \Cref{a}.}''')
        output, _ = convert(source)
        self.assertIn(r'[^imported-1]: See \Cref{a}.', output)
        self.assertNotIn('@@PROOFREF', output)

    def test_unknown_environment_and_unresolved_reference_are_reported(self):
        source = document(r'''\section{One}
\begin{mystery}Important content.\end{mystery}
See \Cref{missing}.''')
        output, warnings = convert(source)
        self.assertIn(r'\begin{mystery}Important content.\end{mystery}', output)
        self.assertIn('&#92;Cref{missing}', output)
        self.assertTrue(any('unsupported environment' in message for message in warnings))
        self.assertTrue(any('unresolved' in message for message in warnings))

    def test_invalid_or_missing_document_is_not_silently_converted(self):
        with self.assertRaises(ValueError):
            convert('Nothing to import.')
        output, warnings = convert(document(r'\begin{lemma}Unclosed.'))
        self.assertIn(r'\begin{lemma}Unclosed.', output)
        self.assertTrue(any('unclosed or mismatched' in message for message in warnings))

    def test_nested_statements_are_preserved_and_reported(self):
        source = document(r'''\section{One}
\begin{theorem}\label{outer}
\begin{lemma}\label{inner}Nested content.\end{lemma}
\end{theorem}''')
        output, warnings = convert(source)
        self.assertIn(r'\begin{lemma}\label{inner}Nested content.\end{lemma}', output)
        self.assertEqual(output.count('::: proof-ref'), 1)
        self.assertTrue(any('nested lemma' in message for message in warnings))

    def test_comments_do_not_confuse_document_boundaries(self):
        output, _ = convert('% \\begin{document}\n' + document('Real content.'))
        self.assertIn('Real content.', output)
        self.assertNotIn('\\begin{document}', output)

    def test_cli_does_not_overwrite_source_or_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            source, output = path / 'proof.tex', path / 'proof.md'
            original = document(r'\section{Example}A proof.')
            source.write_text(original)
            command = [sys.executable, str(ROOT / 'import_tex.py'), str(source), '-o', str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn('A proof.', output.read_text())
            output.write_text('Do not overwrite')
            second = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_text(), 'Do not overwrite')
            self.assertEqual(source.read_text(), original)

    def test_macro_mismatches_are_reported(self):
        source = document(r'\section{One}$\E(X)$', r'\newcommand{\E}{\mathbb{E}}')
        _, warnings = convert(source, {r'\E': r'\mathcal{E}'})
        self.assertTrue(any('differs from the site macro file' in w for w in warnings))

    def test_bibliography_and_forward_citations(self):
        source = document(r'''\section{One}
See \cite[page 7]{first,second}. A note\footnote{See \cite{second}.}
\begin{thebibliography}{99}
\bibitem{first} Author \& Co. \emph{Book}. \url{https://example.org/book}.
\bibitem[Name 2020]{second} Another author.
\end{thebibliography}''')
        output, warnings = convert(source)
        self.assertIn('## References', output)
        self.assertIn('<span id="bib-first"></span>', output)
        self.assertIn('<a href="#bib-first">1</a>', output)
        self.assertIn('<a href="#bib-second">Name 2020</a>', output)
        self.assertIn('page 7]', output)
        self.assertIn('*Book*', output)
        self.assertIn('<https://example.org/book>', output)
        self.assertIn('[^imported-1]: See [<a href="#bib-second">Name 2020</a>].', output)
        self.assertFalse(any('bibliography' in warning or 'citation' in warning for warning in warnings))

    def test_bibliography_missing_duplicate_and_invalid_entries_are_reported(self):
        source = document(r'''\section{One}See \cite{missing,first}.
\begin{thebibliography}{9}
\bibitem{first} First text.
\bibitem{first} Duplicate text.
\bibitem Invalid entry.
\end{thebibliography}''')
        output, warnings = convert(source)
        self.assertIn('?missing', output)
        self.assertIn('Duplicate text.', output)
        self.assertIn('Invalid entry.', output)
        self.assertTrue(any('unresolved citation key' in warning for warning in warnings))
        self.assertTrue(any('duplicate bibliography key' in warning for warning in warnings))
        self.assertTrue(any('invalid bibliography entry' in warning for warning in warnings))

    def test_unknown_bibliography_url_is_kept_as_text(self):
        source = document(r'''\begin{thebibliography}{9}
\bibitem{one} Text at \url{example.org}.
\end{thebibliography}''')
        output, warnings = convert(source)
        self.assertIn('example.org', output)
        self.assertNotIn('<example.org>', output)
        self.assertTrue(any('shown as text' in warning for warning in warnings))

    def test_immediate_proof_is_attached_without_moving_it(self):
        source = document(r'''\section{One}
\begin{lemma}\label{a}A statement.\end{lemma}
% A comment does not interrupt adjacency.
\begin{proof}The proof of A.\end{proof}
After the proof.''')
        output, warnings = convert(source)
        self.assertIn('<div class="proof-details" data-reference-id="a" markdown="1">', output)
        self.assertLess(output.index('A statement.'), output.index('The proof of A.'))
        self.assertLess(output.index('The proof of A.'), output.index('After the proof.'))
        self.assertFalse(any('proof target' in warning for warning in warnings))

    def test_named_proof_can_follow_other_content_or_precede_statement(self):
        source = document(r'''\section{One}
\begin{proof}[Proof of \Cref{later result}]Named proof.\end{proof}
Other text.
\begin{theorem}\label{later result}A result.\end{theorem}''')
        output, warnings = convert(source)
        self.assertIn('<div class="proof-details" data-reference-id="later-result" markdown="1">', output)
        self.assertIn('Named proof.', output)
        self.assertFalse(any('proof target' in warning for warning in warnings))

    def test_ambiguous_and_unknown_proofs_remain_unattached(self):
        source = document(r'''\section{One}
\begin{lemma}\label{a}A.\end{lemma}
\begin{lemma}\label{b}B.\end{lemma}
\begin{proof}Which lemma?\end{proof}
\begin{proof}[Proof of \Cref{missing}]Unknown target.\end{proof}
\begin{lemma}\label{c}C.\end{lemma}
Intervening text.
\begin{proof}Unclear target.\end{proof}''')
        output, warnings = convert(source)
        self.assertNotIn('class="proof-details"', output)
        for text in ('Which lemma?', 'Unknown target.', 'Unclear target.'):
            self.assertIn(text, output)
        self.assertTrue(any('proof target is ambiguous' in warning for warning in warnings))
        self.assertTrue(any("proof target 'missing'" in warning for warning in warnings))

    def test_proof_inside_statement_is_not_nested_in_html(self):
        source = document(r'''\section{One}
\begin{lemma}\label{a}Statement.
\begin{proof}Proof inside.\end{proof}\end{lemma}''')
        output, _ = convert(source)
        self.assertIn('**Proof.** Proof inside.', output)
        self.assertNotIn('class="proof-details"', output)


if __name__ == '__main__':
    unittest.main()
