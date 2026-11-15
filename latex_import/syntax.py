"""Balanced LaTeX groups and environments, with source text left intact."""
import re

ENV_TOKEN = re.compile(r"\\(begin|end)\{([^{}]+)\}")
COMMAND = re.compile(r"\\([A-Za-z]+\*?|.)", re.DOTALL)
LABEL = re.compile(r"\\label\{([^{}]+)\}")


def mask_comments(text):
    """Replace comments by spaces while keeping offsets and line breaks."""
    result = list(text)
    comment = False
    for i, char in enumerate(text):
        if char == "\n":
            comment = False
        elif comment:
            result[i] = " "
        elif char == "%":
            backslashes = 0
            j = i - 1
            while j >= 0 and text[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                result[i] = " "
                comment = True
    return "".join(result)


def group(text, pos, left="{", right="}"):
    """Read a balanced argument; preserve escaped delimiters."""
    if pos >= len(text) or text[pos] != left:
        return None
    depth, start, i = 1, pos + 1, pos + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == left:
            depth += 1
        elif text[i] == right:
            depth -= 1
            if not depth:
                return text[start:i], i + 1
        i += 1
    return None


def argument(text, pos, left="{", right="}"):
    while pos < len(text) and text[pos] in " \t\n":
        pos += 1
    return group(text, pos, left, right)


def environment(text, start):
    first = ENV_TOKEN.match(text, start)
    if not first or first.group(1) != "begin":
        return None
    stack = [first.group(2)]
    for match in ENV_TOKEN.finditer(mask_comments(text), first.end()):
        if match.group(1) == "begin":
            stack.append(match.group(2))
        elif not stack or stack.pop() != match.group(2):
            return None
        if not stack:
            return first.group(2), text[first.end():match.start()], match.end(), first.end()
    return None
