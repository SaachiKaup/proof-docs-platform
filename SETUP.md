# Getting started with Proof Notes

Proof Notes turns Markdown files into a website for mathematical writing. You can
write proofs with LaTeX-style mathematics, offer optional background for readers
with different experience, and link to definitions or lemmas that open beside
the proof. The Markdown files are the source of truth; the website and the
editor's preview are generated from them.

## 1. Install the tools

You need Python 3.10 or later, Node.js and npm, and a terminal. Check that they
are available with:

```sh
python3 --version
node --version
npm --version
```

Python builds the site and runs the editor. npm installs KaTeX, which renders
the mathematics during the build. An internet connection is needed to install
the dependencies. Obtain a copy of this project, open a terminal, and change
into its root directory (the directory containing `README.md` and `mkdocs.yml`).

On macOS or Linux, run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci
```

On Windows, using PowerShell, run:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
npm ci
```

The remaining commands use the macOS/Linux Python path. On Windows, replace
`.venv/bin/python` with `.venv\Scripts\python.exe`. You do not need to activate
the virtual environment.

## 2. Start the editor

From the project root, run:

```sh
.venv/bin/python author/server.py
```

Open <http://127.0.0.1:8765/> in your browser. Keep the terminal running while
you work; press `Ctrl+C` in that terminal when you are finished. This server is
for local authoring.

If a topic setup screen appears, create the shared topic list there. The bundled
example chapter uses the IDs `definitions`, `algebra`, and `number-theory`, so
add all three if you are keeping that chapter. Labels can be, for example,
“Definitions”, “Algebra”, and “Number Theory”. If the list already exists,
check or add these entries through **Topics**. An empty list is valid, but the
example chapter will fail validation until its tags are added or removed.

## 3. Create your first proof

1. In the editor, choose an existing page to explore, or select **New page**
   and enter a path such as `chapters/my-proof.md`. Paths use lowercase letters,
   numbers and hyphens, with `/` between folders and a `.md` extension.
2. Write Markdown in the editor. For example:

   ```md
   # My first proof

   ## Claim

   If $n$ is even, then $n^2$ is even.

   **Proof.** Write $n = 2k$ for some integer $k$. Then

   $$
   n^2 = 2(2k^2),
   $$

   so $n^2$ is even.
   ```

3. An initial preview appears when you open or create a page. After editing,
   click **Update preview** to build and inspect the current draft; typing
   does not automatically rebuild it.
4. Click **Save**. Saving validates the whole site first; fix any reported
   errors and try again. A new page is saved under `docs/` and added to
   `mkdocs.yml` navigation. You can edit the navigation labels and order in
   that file later.

The **Topics** panel manages the shared list. Adding a topic saves it
immediately; page edits and topic removals require **Save**. The preview is a
temporary build and does not itself save your page. Keep your own backups or
use version control for the Markdown and configuration files.

## 4. Add explanations and references

Use topic IDs from **Topics** to mark background that a reader may choose to
hide. For example, after adding `algebra`:

```md
::: knowledge tags="algebra"
The distributive law gives $2(a+b) = 2a + 2b$.
:::
```

With multiple comma-separated tags, the explanation collapses only when the
reader selects *all* of them. A **Show explanation** control stays visible so
readers can expand it anyway. Keep essential proof steps outside these blocks. Topic
IDs must exist in `topics.json`; unknown or repeated tags cause a build error.
A knowledge block cannot contain another directive block.

To make a definition or lemma available in a reference card on the same page:

```md
::: proof-ref id="definition-even"
## Definition: Even integer

An integer $n$ is even if $n = 2k$ for some integer $k$.
:::

By [[the definition of evenness|definition-even]], write $n = 2k$.
```

A missing reference causes a build error. Knowledge blocks may be placed inside
`proof-ref` blocks. Normal Markdown links and footnotes work for external
sources. For complete examples, see `docs/chapters/01-even-numbers.md` and
`docs/chapters/groups.md`.

## 5. Build and share the saved site

To check and generate the site from the saved files, run from the project root:

```sh
.venv/bin/python -m mkdocs build --strict
```

The output is in `site/`; it can be uploaded to a static website host. Do not
edit generated files there: change the source and rebuild instead. To browse
the saved site locally, run:

```sh
.venv/bin/python -m mkdocs serve
```

Open <http://127.0.0.1:8000/> and stop the server with `Ctrl+C`. This is
separate from the editor and shows saved files, not an unsaved editor draft.

## Troubleshooting and notes for agents

- Run commands from the project root. If a Python module is missing, install
  `requirements.txt` into `.venv` and use that environment's Python.
- If mathematics fails to build because KaTeX is unavailable, run `npm ci`
  from the root and retry. Both Python and npm dependencies are needed.
- If `topics.json` is missing, start the editor and complete topic setup before
  building. It contains a JSON array of `{ "id": "...", "label": "..." }`
  objects; IDs must be unique, start with a lowercase letter, and contain only
  lowercase letters, digits, and hyphens. Existing pages' tags must be present.
  Preserve and share this file with the Markdown pages.
- If a build reports an invalid topic or reference, inspect the named page and
  correct the tag or same-page reference. A build validates all pages, so an
  error may come from a different page than the one being edited.
- If a port is already in use, stop the existing local server before starting
  another. The author server uses port 8765; MkDocs serve defaults to 8000.
- Content is in `docs/`, site configuration and navigation in `mkdocs.yml`,
  topic data in `topics.json`, and authoring/build logic in `author/` and
  `plugins/`. Preserve existing user edits. Do not treat `site/` as source.
- For changes to the application, see the checks in `README.md`. The npm
  `test` script is a placeholder; use the listed Python and Node commands instead.
