"""Render the supported subset, reporting unsupported source constructs."""
import re
from html import escape

from .syntax import COMMAND, LABEL, argument, environment, mask_comments
from .context import register, slug, warn
from .bibliography import bibliography
from .proofs import record_statement, wrap_proof

ENVIRONMENTS = {
    "theorem": "theorem", "lemma": "lemma", "prop": "proposition",
    "proposition": "proposition", "defn": "definition", "definition": "definition",
    "corollary": "corollary", "remark": "remark", "exa": "example", "example": "example",
}
KNOWLEDGE_TAGS = re.compile(r"[a-z][a-z0-9-]*(?:,[a-z][a-z0-9-]*)*")


def tikz(body, state, offset):
    warn(state, offset, "diagram needs a human-written description and review of its packages and macros")
    names = {name for name in state['macros'] if re.search(re.escape(name) + r"(?![A-Za-z])", body)}
    pending = list(names)
    while pending:
        definition = state['macros'][pending.pop()]
        for name in state['macros']:
            if name not in names and re.search(re.escape(name) + r"(?![A-Za-z])", definition):
                names.add(name)
                pending.append(name)
    setup = []
    for name in sorted(names):
        definition = state['macros'][name]
        parameters = [int(n) for n in re.findall(r"#([1-9])", definition)]
        args = "".join(f"#{i}" for i in range(1, max(parameters, default=0) + 1))
        setup.append(f"\\def{name}{args}{{{definition}}}")
    return ("\n\n<figure class=\"tikz-diagram\">\n"
            "<script type=\"text/tikz\" data-tex-packages='{" + '"tikz-cd":"","amssymb":""' + "}'>\n"
            + ("\n".join(setup) + "\n" if setup else "") + body.strip() + "\n</script>\n"
            "<figcaption>Diagram description needed.</figcaption>\n</figure>\n\n")


def display(body, state, offset, numbered=False):
    labels = LABEL.findall(body)
    body = LABEL.sub("", body).strip()
    tag, anchor = "", ""
    if numbered:
        state['equation'] += 1
        tag = f"\\tag{{{state['equation']}}}"
        if labels:
            identifier = slug("eq-" + labels[0], state)
            if register(state, labels[0], "equation", identifier, str(state['equation']), offset):
                anchor = f'<span id="{identifier}"></span>\n\n'
    elif labels:
        warn(state, offset, "label in an unnumbered display needs manual review")
    if len(labels) > 1:
        warn(state, offset, "multiple labels in one display need manual review")
    match = re.search(r"\\begin\{tikzcd\}.*?\\end\{tikzcd\}", body, re.DOTALL)
    if match:
        before = mask_comments(body[:match.start()]).strip()
        after = mask_comments(body[match.end():]).strip().strip('.')
        if before or after:
            warn(state, offset, "content surrounding diagram needs manual review")
        extra = f"\n\n<pre>{escape(before + chr(10) + after)}</pre>\n\n" if before or after else ""
        return "\n\n" + anchor + tikz(match.group(), state, offset) + extra + (f"\n({state['equation']})\n" if numbered else "")
    return "\n\n" + anchor + "$$\n" + body + tag + "\n$$\n\n"


def render(text, state, base=0):
    output, i = [], 0
    while i < len(text):
        absolute = base + i
        if text[i] == "%" and (i == 0 or text[i-1] != "\\"):
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
            continue
        if text.startswith("$$", i):
            end = text.find("$$", i + 2)
            if end < 0:
                warn(state, absolute, "unclosed display math; original text preserved")
                output.append(text[i:]); break
            output.append(display(text[i+2:end], state, absolute))
            i = end + 2; continue
        if text[i] == "$":
            end = i + 1
            while end < len(text):
                if text[end] == "\\": end += 2; continue
                if text[end] == "$": break
                end += 1
            if end == len(text):
                warn(state, absolute, "unclosed inline math; original text preserved")
                output.append(text[i:]); break
            output.append(text[i:end+1]); i = end + 1; continue
        if text.startswith("\\begin{", i):
            found = environment(text, i)
            if not found:
                warn(state, absolute, "unclosed or mismatched environment; remaining source preserved")
                output.append(text[i:]); break
            name, inner, end, inner_start = found
            if name == "knowledge":
                tags = argument(inner, 0)
                tag_ids = re.sub(r"\s+", "", tags[0]) if tags else ""
                if not KNOWLEDGE_TAGS.fullmatch(tag_ids) or state['in_statement']:
                    warn(state, absolute, "knowledge environment needs comma-separated lowercase topic IDs")
                    output.append(text[i:end])
                else:
                    content = render(inner[tags[1]:], state, base + inner_start + tags[1])
                    output.append(f'\n\n::: knowledge tags="{tag_ids}"\n{content.strip()}\n:::\n\n')
            elif name in ENVIRONMENTS:
                if state['in_statement']:
                    warn(state, absolute, f"nested {name} cannot be represented as a reference card; source preserved")
                    output.append(text[i:end])
                    i = end
                    continue
                kind = ENVIRONMENTS[name]
                label_match = LABEL.search(inner)
                label = label_match.group(1) if label_match else f"imported-{kind}-{state['section']}-{state['statement'] + 1}"
                if not label_match:
                    warn(state, absolute, f"{kind} has no label; generated {label!r}")
                    inner = "\\label{" + label + "}\n" + inner
                state['statement'] += 1
                identifier = slug(label, state)
                if not state['section']:
                    warn(state, absolute, "statement before a numbered section cannot use automatic reference cards")
                    output.append(f"\n\n### {kind.capitalize()}\n\n" + render(LABEL.sub('', inner, count=1), state, base + inner_start) + "\n\n")
                elif register(state, label, kind, identifier, f"{state['section']}.{state['statement']}", absolute):
                    state['in_statement'] = True
                    content = render(inner, state, base + inner_start).strip()
                    state['in_statement'] = False
                    output.append(f'\n\n::: proof-ref id="{identifier}" type="{kind}"\n' + content + "\n:::\n\n")
                    record_statement(state, label, absolute, base + end)
                else:
                    output.append(f"\n\n### {kind.capitalize()}\n\n" + render(LABEL.sub('', inner, count=1), state, base + inner_start) + "\n\n")
            elif name in ("equation", "equation*", "align", "align*"):
                if name.startswith("align"):
                    if name == "align": warn(state, absolute, "numbered align rows need manual numbering review")
                    inner = "\\begin{aligned}\n" + inner.strip() + "\n\\end{aligned}"
                output.append(display(inner, state, absolute, name == "equation"))
            elif name == "tikzcd":
                output.append(tikz(text[i:end], state, absolute))
            elif name == "thebibliography":
                output.append(bibliography(inner, state, base + inner_start, render))
            elif name == "proof":
                option = argument(inner, 0, "[", "]")
                if option:
                    heading, rest = option[0], inner[option[1]:]
                    content = "**" + render(heading, state, base + inner_start + 1) + ".**\n\n" + render(rest, state, base + inner_start + option[1]).strip()
                else:
                    content = "**Proof.** " + render(inner, state, base + inner_start).strip()
                output.append("\n\n" + wrap_proof(content, option[0] if option else None, state, absolute) + "\n\n")
            elif name in ("itemize", "enumerate"):
                converted = render(inner, state, base + inner_start)
                output.append("\n\n" + re.sub(r"\\item\s*", "\n- " if name == "itemize" else "\n1. ", converted).strip() + "\n\n")
            else:
                warn(state, absolute, f"unsupported environment {name!r}; source preserved")
                output.append(text[i:end])
            i = end; continue
        if text[i] == "\\":
            match = COMMAND.match(text, i)
            if not match:
                output.append(text[i]); i += 1; continue
            cmd, after = match.group(1), match.end()
            arg = argument(text, after)
            if cmd in ("section", "subsection", "subsubsection") and arg:
                level = {"section": 2, "subsection": 3, "subsubsection": 4}[cmd]
                if cmd == "section": state['section'] += 1; state['statement'] = 0
                prefix = f"{state['section']}. " if cmd == "section" else ""
                output.append("\n\n" + "#" * level + " " + prefix + render(arg[0], state, absolute + (after-i) + 1).strip() + "\n\n")
                i = arg[1]; continue
            if cmd in ("cref", "Cref", "ref", "eqref") and arg:
                state['references'].append((cmd, arg[0], absolute))
                output.append(f"@@PROOFREF{len(state['references'])-1}@@")
                i = arg[1]; continue
            if cmd == "cite":
                option = argument(text, after, "[", "]")
                keys = argument(text, option[1] if option else after)
                if keys:
                    state['citations'].append((keys[0], option[0] if option else "", absolute))
                    output.append(f"@@PROOFCITE{len(state['citations'])-1}@@")
                    i = keys[1]; continue
                warn(state, absolute, "unsupported citation syntax; source preserved")
                output.append(match.group()); i = after; continue
            if cmd == "url" and arg:
                url = arg[0].strip()
                if re.fullmatch(r"https?://[^\s<>]+", url):
                    output.append(f"<{url}>")
                else:
                    output.append(escape(url))
                    warn(state, absolute, f"URL {url!r} has no supported http(s) scheme; shown as text")
                i = arg[1]; continue
            if cmd == "label" and arg:
                output.append("\\label{" + arg[0] + "}")
                i = arg[1]; continue
            if cmd in ("hl", "textbf", "emph", "textit") and arg:
                mark = "**" if cmd in ("hl", "textbf") else "*"
                output.append(mark + render(arg[0], state, absolute + (after-i) + 1) + mark)
                i = arg[1]; continue
            if cmd == "footnote" and arg:
                state['footnotes'].append(render(arg[0], state, absolute + (after-i) + 1))
                output.append(f"[^imported-{len(state['footnotes'])}]")
                i = arg[1]; continue
            if cmd == "item":
                output.append("\\item "); i = after; continue
            if cmd in ("input", "include", "bibliography", "bibliographystyle", "href"):
                warn(state, absolute, f"\\{cmd} requires manual review; source preserved")
            elif cmd not in ("\\", "%", "&", "_", "#", "{", "}"):
                warn(state, absolute, f"unsupported text command \\{cmd}; source preserved")
            output.append(match.group()); i = after; continue
        output.append(text[i]); i += 1
    return "".join(output)
