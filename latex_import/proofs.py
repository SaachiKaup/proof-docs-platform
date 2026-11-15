"""Associate proofs with statements when the source makes the target clear."""
import re

from .context import warn
from .syntax import mask_comments

NAMED_PROOF = re.compile(r'^\s*(?:proof\s+of\s+)?\\(?:Cref|cref|ref)\{([^{}]+)\}\s*\.?\s*$', re.IGNORECASE)


def record_statement(state, label, start, end):
    pending = state['pending_statements']
    if pending and mask_comments(state['source'][pending[-1][1]:start]).strip():
        pending.clear()
    pending.append((label, end))


def wrap_proof(content, heading, state, offset):
    if state['in_statement']:
        return content
    if heading is not None:
        match = NAMED_PROOF.fullmatch(heading)
        label = match.group(1) if match and ',' not in match.group(1) else None
    else:
        pending = state['pending_statements']
        adjacent = pending and not mask_comments(state['source'][pending[-1][1]:offset]).strip()
        label = pending[0][0] if adjacent and len(pending) == 1 else None
    state['pending_statements'].clear()
    if not label:
        warn(state, offset, 'proof target is ambiguous; proof remains in the document')
        return content
    state['proofs'].append((label, offset))
    index = len(state['proofs']) - 1
    return f'@@PROOFDETAILSTART{index}@@\n\n{content}\n\n@@PROOFDETAILEND{index}@@'


def resolve_proofs(text, state):
    for index, (label, offset) in enumerate(state['proofs']):
        target = state['labels'].get(label)
        if target and target[0] != 'equation':
            opening = f'<div class="proof-details" data-reference-id="{target[1]}" markdown="1">'
            closing = '</div>'
        else:
            warn(state, offset, f'proof target {label!r} does not identify a statement; proof remains in the document')
            opening = closing = ''
        text = text.replace(f'@@PROOFDETAILSTART{index}@@', opening)
        text = text.replace(f'@@PROOFDETAILEND{index}@@', closing)
    return text
