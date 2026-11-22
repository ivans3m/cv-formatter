"""Relevance scoring for CV bullets against JD keywords."""

from __future__ import annotations

import re

from cvfmt.tailor.keywords import tokenize


def score_text(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 0.0
    hay = set(tokenize(text))
    hits = sum(1 for kw in keywords if kw in hay or kw.replace("-", "") in hay)
    # Phrase boost: multi-token keywords
    lower = text.lower()
    for kw in keywords:
        if len(kw) > 4 and kw in lower:
            hits += 0.5
    return hits


def score_bullet(bullet: str, keywords: list[str]) -> float:
    return score_text(bullet, keywords)