"""Conversion state and simple preamble definitions."""
import re

from .syntax import argument


def new_state(source):
    return {"source": source, "labels": {}, "diagnostics": [], "section": 0,
            "statement": 0, "equation": 0, "ids": set(), "references": [],
            "footnotes": [], "macros": {}, "in_statement": False,
            "bibliography": {}, "bib_count": 0, "citations": [],
            "pending_statements": [], "proofs": []}


def warn(state, offset, message):
    line = state['source'].count("\n", 0, offset) + 1
    state['diagnostics'].append(f"line {line}: {message}")


def slug(label, state):
    base = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-") or "statement"
    if not base[0].isalpha():
        base = "ref-" + base
    result, n = base, 2
    while result in state['ids']:
        result, n = f"{base}-{n}", n + 1
    state['ids'].add(result)
    return result


def register(state, label, kind, identifier, number, offset):
    if label in state['labels']:
        warn(state, offset, f"duplicate label {label!r}; references require review")
        return False
    state['labels'][label] = (kind, identifier, number)
    return True


def definitions(preamble):
    """Extract simple macro definitions for comparison, not direct execution."""
    found = {}
    pattern = re.compile(r"\\(?:newcommand|renewcommand)\s*(?:\{(\\[A-Za-z]+)\}|(\\[A-Za-z]+))")
    for match in pattern.finditer(preamble):
        name = match.group(1) or match.group(2)
        pos = match.end()
        optional = argument(preamble, pos, "[", "]")
        if optional:
            pos = optional[1]
            if argument(preamble, pos, "[", "]"): continue
        body = argument(preamble, pos)
        if body and "\n" not in body[0] and ":" not in body[0]:
            found[name] = body[0]
    for match in re.finditer(r"\\DeclareMathOperator\s*\{(\\[A-Za-z]+)\}\s*\{([^{}]+)\}", preamble):
        found[match.group(1)] = r"\operatorname{" + match.group(2) + "}"
    return found
