# Proof Notes

Proof Notes is a small documentation site for mathematical proofs. An author
writes a proof in Markdown and marks optional explanations by topic. Readers
choose topics they already understand, and matching explanations disappear
while the rest of the page reflows. Definitions and lemmas can also open in
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

An explanation is hidden only when the reader selects **all** its tags. For
example, the passage above stays visible if the reader knows algebra but has
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

## How the pieces fit together

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
TikZJax renders it in the reader's browser; the browser needs JavaScript and
network access to TikZJax's assets. Add a text description beside each diagram
so its meaning remains available when the diagram cannot be displayed. Any
custom commands used in a diagram also need definitions inside its TikZ wrapper;
the KaTeX macro file does not supply definitions to TikZJax.

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
