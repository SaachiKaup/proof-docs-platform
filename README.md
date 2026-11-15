# Proof Notes

Proof Notes is a small documentation site for mathematical proofs. An author
writes a proof in Markdown and marks optional explanations by topic. Readers
choose topics they already understand, and matching explanations collapse
behind a **Show explanation** control. Definitions and lemmas can also open in
reference cards beside the proof.

```text
Author writes Markdown + topic labels
                ↓
MkDocs validates and renders the pages
                ↓
Reader views the site and selects known topics
```

The local editor is a convenient way to edit and preview those Markdown files;
the files themselves remain the source of truth. The generated site is a
separate companion to any required LaTeX/PDF submission.
The snippets below illustrate the platform's authoring syntax; they are not
the actual report.

## Start the authoring editor

From the project directory, install the dependencies once:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm install
```

Start the local editor:

```sh
.venv/bin/python author/server.py
```

Open <http://127.0.0.1:8765/>. Choose or create a page, write Markdown, and
use **Topics** to manage the shared topic list. A preview appears when a page
opens; click **Update preview** to refresh it after editing. Added topics are
saved immediately, while page edits and topic removals require **Save**. After
a successful save, **Open saved site** opens that saved page in a new tab.
Drag the divider to resize the panes. Stop the server with `Ctrl+C`.

The topic ID is optional: leaving it blank generates one from the topic name,
such as `number-theory` for “Number Theory”. Enter an ID to override it.

If `topics.json` is missing, the editor first offers a setup screen to create
the topic list. You can start with an empty list and add topics later. If the
file already exists, the editor opens directly and uses that list.

The editor server is for local authoring, not public hosting. The preview is
built from the draft; the saved-site button opens a separate local copy of the
last saved version. Both are available only while the editor server is running.

## Write a proof

### Import a LaTeX draft

From the project directory, write a new Markdown page with:

```sh
.venv/bin/python import_tex.py ../inverted.tex -o docs/chapters/imported-proof.md
```

The importer never changes the TeX file or overwrites an existing output.
It prints diagnostics to the terminal: review them and the generated page
before sharing it. Open the new page in the author editor to preview it; saving
it there adds it to the site navigation. Use a different output filename for
another import so that edits are not lost.

This is a first, partial converter. It handles common sections, statement and
proof environments, explicitly tagged `knowledge` environments, simple equations, references, footnotes, lists, in-file
`thebibliography` entries, basic `\cite` links and TikZ commutative diagrams.
It assumes shared theorem counters within each section
and globally numbered equations; confirm numbering against the PDF. It reports
unsupported constructs, missing or conflicting macro definitions and diagrams
requiring a written description. It does not automatically change the global
KaTeX macro file, infer optional topics, verify the math or guarantee that the
full LaTeX preamble and every package will render correctly. `\input` and
other external files are not imported. Citation styles and commands beyond
basic `\cite` are not automatically reproduced; inspect diagnostics and the
original for material that needs manual attention.

The importer links an immediately following proof to its statement, or uses
an explicit heading such as `\begin{proof}[Proof of \Cref{label}]`. Readers
can expand that proof in the reference card. If a proof's target is ambiguous,
the proof stays in the page and the importer reports it for review.

Mark optional background in TeX with `\begin{knowledge}{algebra}` and
`\end{knowledge}`. Topic IDs must already exist in `topics.json`. The importer
converts this to the same `::: knowledge` block used in Markdown, including the
reader's **Show explanation** control when its tags are selected. Add a
matching `knowledge` environment definition to the TeX preamble if compiling
the source to PDF as well.

### Edit a page

Pages live in `docs/`, and the shared topic list lives in `topics.json`. Use
Markdown for prose and headings, and LaTeX-style math such as `$x^2$` or a
`$$` display block. See `docs/chapters/groups.md` for a commutative square.
The imported topological-extensions draft uses the `group-cohomology` topic;
add that ID to the topic list if setting up the project with a new catalog.
Its Markdown is an adapted copy, not automatically synchronized with the
original `inverted.tex`.

Wrap optional background in a knowledge block using IDs from the topic list:

```md
::: knowledge tags="algebra,number-theory"
Optional background written in Markdown and $x^2$ mathematics.
:::
```

An explanation is collapsed only when the reader selects **all** its tags. Its
**Show explanation** control remains available, so readers can open it anyway.
For example, the passage above stays visible if the reader knows algebra but has
not selected number theory. Unknown tags fail the build. Reader selections
are stored in that browser; untagged text stays visible, and all text remains
visible when JavaScript is unavailable. Keep essential proof steps outside
optional blocks.

To make a definition or lemma available as a reference card, give it an ID
and refer to it elsewhere on the same page:

```md
::: proof-ref id="lemma-even-square"
## Lemma: Squaring preserves evenness
...
:::

By [[the lemma|lemma-even-square]], the claim follows.
```

A missing reference stops the build. References currently work within the
same page. External sources can use normal Markdown links and footnotes.
Knowledge blocks may occur inside `proof-ref` blocks, but cannot themselves
contain another directive block.

A paragraph beginning with `**Proof.**` inside a reference block appears
under **Open full section** in its card. For a proof that is elsewhere on the
page, associate it explicitly with the card while leaving it in the main text:

```md
<div class="proof-details" data-reference-id="lemma-even-square" markdown="1">

**Proof.** The proof goes here.

</div>
```

The card expands in place; it does not navigate away from the reader's position.

## How the pieces fit together

The topological-extensions page also demonstrates a limited LaTeX-style
reference syntax. Within a manually numbered `## 2. ...` section, a typed
block such as `::: proof-ref id="example" type="lemma"` can contain
`\label{original label}`. Elsewhere on the same page, `\Cref{original label}`
opens its reference card. Typed lemmas, theorems and propositions share a
counter that resets at each numbered section; their headings and references
are generated together. The visible reference is just the number; the card
retains the full statement type and number. This is a small website implementation, not the LaTeX
`cleveref` package: equation references, multiple labels, custom counters,
cross-page references and LaTeX's cleveref formatting are not yet supported.


| Part | Responsibility |
| --- | --- |
| `docs/*.md` and `docs/chapters/` | The author's pages, including proof text, topic tags, and references. |
| `topics.json` | Topic IDs and names shared across the site. |
| `author/` | The local editing interface, server, saving, and temporary previews. |
| `mkdocs.yml` | Site navigation, theme, Markdown extensions, and build configuration. |
| `plugins/topic_checker.py` | Validates topic tags and builds the reader's topic selector. |
| `plugins/proof_references.py` | Builds reference cards and prepares math for KaTeX. |
| `docs/javascripts/` | Reader-side topic filtering and reference-card interaction. |
| `docs/stylesheets/` | Presentation of the generated reader site. |
| `tests/` | Checks for build errors, references, topic handling, and filtering. |
| `site/` | Generated website output; rebuild it instead of editing it by hand. |

Python performs validation and generates the pages at build time. JavaScript
runs in the reader's browser to change which explanations and cards are shown.
Math is rendered during the build using KaTeX, installed through npm.

### LaTeX macros and TikZ diagrams

Define shared KaTeX math macros in `docs/tex-macros.txt`, one per line, for
example `\E:\mathbb{E}` or `\Hgp:H_{\text{gp}}^{#1}`. These definitions
apply to every page. They are maintained separately from the original TeX
preamble: changing the `.tex` file does not update them automatically.
KaTeX supports a subset of LaTeX, so check each macro when adding it.

For a TikZ diagram, wrap its original code in a
`<script type="text/tikz">` element, as in the topological extensions page.
The rod2ik TikZJax fork renders it in the reader's browser; the browser needs JavaScript and
network access to TikZJax's assets. Add a text description beside each diagram
so its meaning remains available when the diagram cannot be displayed. Any
custom commands used in a diagram also need definitions inside its TikZ wrapper;
the KaTeX macro file does not supply definitions to TikZJax.
The topological extensions examples load `tikz-cd` and `amssymb` through the
script's `data-tex-packages` attribute. TikZJax's generated SVG uses encoded
font glyphs, so its visible text should not be relied on for copy and paste;
write a meaningful diagram description in the surrounding page.

## Build and check

```sh
.venv/bin/python -m unittest discover -s tests -v
node tests/test_knowledge_ui.js
node tests/test_topic_authoring.js
node tests/test_line_numbers.js
node tests/test_manual_preview.js
node --check author/editor.js
node --check author/pane-resize.js
node --check docs/javascripts/reference-panel.js
node --check docs/javascripts/topic-switch.js
.venv/bin/python -m mkdocs build --strict
```

The finished static site is written to `site/` and can be placed on a static
host. To preview the saved site without the authoring editor, run
`.venv/bin/python -m mkdocs serve` and open <http://127.0.0.1:8000/>.

The notes in `explanations/architecture-and-decisions.md` describe the earlier
reference-card prototype and do not yet cover the full authoring and topic
filtering workflow.
