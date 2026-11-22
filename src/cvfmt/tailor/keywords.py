"""Lightweight job-description keyword extraction (no ML deps)."""

from __future__ import annotations

import re

_STOPWORDS = frozenset(
    """
    a an and are as at be been being but by can could did do does doing for from had has have
    having he her hers him his how i if in into is it its let me more my no nor not of on or our
    out she should so some such than that the their them then there these they this those through
    to too under until up us was we were what when where which while who whom why will with would
    you your yours role team work working years experience required preferred able strong using use
    including include must will responsibilities responsibility qualification qualifications
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+.#/-]*", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]


def extract_keywords(text: str, *, min_len: int = 3) -> list[str]:
    """Return deduplicated JD keywords in rough importance order (frequency)."""
    counts: dict[str, int] = {}
    for tok in tokenize(text):
        if len(tok) < min_len or tok in _STOPWORDS:
            continue
        counts[tok] = counts.get(tok, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [word for word, _ in ranked]