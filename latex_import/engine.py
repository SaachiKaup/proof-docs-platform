"""Top-level conversion: labels, footnotes and compatibility diagnostics."""
import re

from .context import definitions, new_state, warn
from .bibliography import resolve_citation
from .render import render
from .proofs import resolve_proofs
from .syntax import mask_comments


def convert(source, existing_macros=None):
    state = new_state(source)
    visible = mask_comments(source)
    begin = re.search(r"\\begin\{document\}", visible)
    end = re.search(r"\\end\{document\}", visible)
    if not begin or not end or end.start() < begin.end():
        raise ValueError("Expected a complete \\begin{document} ... \\end{document} source")
    preamble = source[:begin.start()]
    body = source[begin.end():end.start()]
    state['macros'] = definitions(preamble)
    if re.search(r"\\(?:input|include)\s*\{", source):
        warn(state, 0, "external input detected; importer does not read external files")
    warn(state, begin.start(), "numbering assumes one shared theorem counter per section and globally numbered equations; verify against the PDF")
    output = render(body, state, begin.end())
    if state['footnotes']:
        output += "\n\n" + "\n".join(f"[^imported-{i}]: {text.strip()}" for i, text in enumerate(state['footnotes'], 1)) + "\n"
    output = resolve_proofs(output, state)
    for index, (keys, note, offset) in enumerate(state['citations']):
        output = output.replace(f"@@PROOFCITE{index}@@", resolve_citation(keys, note, state, offset))
    for index, (command, label, offset) in enumerate(state['references']):
        target = state['labels'].get(label)
        if target and target[0] != "equation" and command in ("cref", "Cref"):
            value = f"\\{command}{{{label}}}"
        elif target:
            kind, identifier, number = target
            caption = f"({number})" if command == "eqref" else number
            value = f"[{caption}](#{identifier})"
        else:
            warn(state, offset, f"unresolved or unsupported \\{command} reference {label!r}")
            value = f"&#92;{command}{{{label}}}"
        output = output.replace(f"@@PROOFREF{index}@@", value)
    extracted = definitions(preamble)
    existing = existing_macros or {}
    for name, definition in extracted.items():
        if re.search(re.escape(name) + r"(?![A-Za-z])", body):
            if name not in existing:
                warn(state, 0, f"math macro {name} is missing from the site macro file; candidate: {name}:{definition}")
            elif existing[name] != definition:
                warn(state, 0, f"math macro {name} differs from the site macro file; review before publishing")
    if "\\DMO" in preamble:
        warn(state, 0, "custom macro-definition helpers such as \\DMO are not extracted")
    title = re.search(r"\\title\s*\{([^{}]*)\}", preamble)
    heading = title.group(1).strip() if title else ""
    return "# " + (heading or "Imported LaTeX document") + "\n\n" + output.strip() + "\n", state['diagnostics']
