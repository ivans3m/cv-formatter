"""Char-budget pruning with lossless archiving into ## Facts."""

from __future__ import annotations

import copy

from cvfmt.models import CVDocument, Entry, Section, canonical_section_key
from cvfmt.tailor.score import score_bullet


def _renderable_char_count(doc: CVDocument) -> int:
    total = 0
    for section in doc.renderable_sections:
        total += sum(len(p) for p in section.paragraphs)
        for bullet in section.bullets:
            total += len(bullet)
        for entry in section.entries:
            total += len(entry.heading)
            total += sum(len(p) for p in entry.paragraphs)
            for bullet in entry.bullets:
                total += len(bullet)
            for sr in entry.sub_roles:
                total += len(sr.title)
                for bullet in sr.bullets:
                    total += len(bullet)
    return total


_LOCALIZED_FACTS_TITLES: dict[str, str] = {
    "nl": "Feiten",
    "de": "Fakten",
    "fr": "Faits",
}


def _ensure_facts(doc: CVDocument) -> Section:
    for section in doc.sections:
        if canonical_section_key(section.title) == "facts":
            return section
    lang_code = (doc.frontmatter.lang or "en").strip().lower().split("-")[0]
    title = _LOCALIZED_FACTS_TITLES.get(lang_code, "Facts")
    facts = Section(title=title, line=0)
    doc.sections.append(facts)
    return facts


def _ensure_archive_entry(facts: Section, target: str) -> Entry:
    heading = f"Archived for {target}"
    for entry in facts.entries:
        if entry.heading.lower() == heading.lower():
            return entry
    entry = Entry(heading=heading, primary=heading, line=0)
    facts.entries.append(entry)
    return entry


def archive_bullet(doc: CVDocument, target: str, context: str, bullet: str) -> None:
    """Park a demoted or stripped bullet under ## Facts -> ### Archived for <target>."""
    facts = _ensure_facts(doc)
    archive_entry = _ensure_archive_entry(facts, target)
    label = context.replace("\n", " ").strip()[:80]
    archive_entry.bullets.append(f"**{label}** — {bullet}")


def prune_to_budget(
    doc: CVDocument,
    *,
    keywords: list[str],
    pages: int,
    tailor_target: str,
) -> list[str]:
    """Drop lowest-scoring bullets until under soft char budget; archive in ## Facts.

    Returns warnings (e.g. summary not rewritten).
    """
    warnings: list[str] = []
    budget = max(2500, pages * 3200)

    def _lowest_bullet() -> tuple[float, str, str, list[str]] | None:
        best: tuple[float, str, str, list[str]] | None = None
        for section in doc.renderable_sections:
            if canonical_section_key(section.title) not in ("experience", "projects"):
                continue
            for bullet in section.bullets:
                sc = score_bullet(bullet, keywords)
                if best is None or sc < best[0]:
                    best = (sc, section.title, bullet, section.bullets)
            for entry in section.entries:
                ctx = f"{section.title} / {entry.heading}"
                for bullet in entry.bullets:
                    sc = score_bullet(bullet, keywords)
                    if best is None or sc < best[0]:
                        best = (sc, ctx, bullet, entry.bullets)
                for sr in entry.sub_roles:
                    ctx_sr = f"{ctx} / {sr.title}"
                    for bullet in sr.bullets:
                        sc = score_bullet(bullet, keywords)
                        if best is None or sc < best[0]:
                            best = (sc, ctx_sr, bullet, sr.bullets)
        return best

    while _renderable_char_count(doc) > budget:
        pick = _lowest_bullet()
        if pick is None:
            break
        _sc, ctx, bullet, bucket = pick
        if bullet not in bucket:
            break
        bucket.remove(bullet)
        archive_bullet(doc, tailor_target, ctx, bullet)

    if _renderable_char_count(doc) > budget:
        warnings.append("SUMMARY_BUDGET: Document still exceeds soft page budget after bullet pruning.")

    return warnings


def reorder_by_relevance(doc: CVDocument, keywords: list[str]) -> None:
    for section in doc.renderable_sections:
        canon = canonical_section_key(section.title)
        if canon in ("experience", "projects"):
            section.bullets.sort(key=lambda b: score_bullet(b, keywords), reverse=True)
            for entry in section.entries:
                entry.bullets.sort(key=lambda b: score_bullet(b, keywords), reverse=True)
                for sr in entry.sub_roles:
                    sr.bullets.sort(key=lambda b: score_bullet(b, keywords), reverse=True)
            section.entries.sort(
                key=lambda e: max(
                    [score_bullet(b, keywords) for b in e.bullets]
                    + [score_bullet(b, keywords) for sr in e.sub_roles for b in sr.bullets]
                    or [0.0]
                ),
                reverse=True,
            )
        elif canon == "skills":
            section.bullets = _reorder_skill_lines(section.bullets, keywords)


def _reorder_skill_lines(bullets: list[str], keywords: list[str]) -> list[str]:
    import re

    out: list[str] = []
    skill_line = re.compile(r"^\*\*([^:*]+):?\*\*:?\s*(.+)$")
    for bullet in bullets:
        m = skill_line.match(bullet)
        if not m:
            out.append(bullet)
            continue
        label, rhs = m.group(1), m.group(2)
        items = [i.strip() for i in rhs.split(",") if i.strip()]

        def item_score(item: str) -> float:
            return score_bullet(item, keywords)

        items.sort(key=item_score, reverse=True)
        out.append(f"**{label}:** {', '.join(items)}")
    return out


def copy_document(doc: CVDocument) -> CVDocument:
    return copy.deepcopy(doc)