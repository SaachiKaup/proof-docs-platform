"""Convert an in-file LaTeX bibliography to linked Markdown entries."""
import re
from html import escape

from .context import slug, warn
from .syntax import argument, mask_comments

BIBITEM = re.compile(r"\\bibitem(?![A-Za-z])")


def bibliography(text, state, base, render):
    width = argument(text, 0)
    if not width:
        warn(state, base, "bibliography is missing its width argument; source preserved")
        return "\\begin{thebibliography}" + text + "\\end{thebibliography}"
    visible = mask_comments(text)
    matches = list(BIBITEM.finditer(visible, width[1]))
    if not matches:
        warn(state, base, "bibliography has no recognized entries; source preserved")
        return "\\begin{thebibliography}" + text + "\\end{thebibliography}"
    prefix = text[width[1]:matches[0].start()]
    result = ['\n\n## References\n\n']
    if mask_comments(prefix).strip():
        warn(state, base + width[1], "text before first bibliography entry preserved")
        result.append(render(prefix, state, base + width[1]) + '\n\n')
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        optional = argument(text, match.end(), '[', ']')
        key_arg = argument(text, optional[1] if optional else match.end())
        if not key_arg or not key_arg[0].strip():
            warn(state, base + match.start(), "invalid bibliography entry; source preserved")
            result.append('<pre>' + escape(text[match.start():end]) + '</pre>\n\n')
            continue
        key = key_arg[0].strip()
        state['bib_count'] += 1
        label = optional[0].strip() if optional else str(state['bib_count'])
        if optional and re.search(r"[\\{}]", label):
            warn(state, base + match.start(), f"custom bibliography label {label!r} needs formatting review")
        identifier = slug('bib-' + key, state)
        if key in state['bibliography']:
            warn(state, base + match.start(), f"duplicate bibliography key {key!r}; citations target the first entry")
        else:
            state['bibliography'][key] = (identifier, label)
        content = render(text[key_arg[1]:end], state, base + key_arg[1]).strip()
        result.append(f'<span id="{identifier}"></span>\n\n**[{escape(label)}]** {content}\n\n')
    return ''.join(result)


def resolve_citation(keys, note, state, offset):
    entries = []
    for key in (part.strip() for part in keys.split(',')):
        target = state['bibliography'].get(key)
        if not key or target is None:
            warn(state, offset, f"unresolved citation key {key!r}")
            entries.append('?' + escape(key))
        else:
            identifier, label = target
            entries.append(f'<a href="#{identifier}">{escape(label)}</a>')
    suffix = ', ' + escape(note) if note else ''
    return '[' + ', '.join(entries) + suffix + ']'
