"""Deterministic strict tailoring pipeline (no LLM)."""

from __future__ import annotations

from cvfmt.models import CURRENT_SCHEMA, CVDocument, is_aspirational_bullet
from cvfmt.tailor.keywords import extract_keywords
from cvfmt.tailor.prune import archive_bullet, copy_document, prune_to_budget, reorder_by_relevance


def _strip_aspirational(doc: CVDocument, *, tailor_target: str) -> int:
    """Remove aspirational bullets from renderable sections and archive them in ## Facts."""
    stripped = 0
    for section in doc.renderable_sections:
        kept_sec: list[str] = []
        for bullet in section.bullets:
            if is_aspirational_bullet(bullet):
                archive_bullet(doc, tailor_target, f"{section.title} (Aspirational)", bullet)
                stripped += 1
            else:
                kept_sec.append(bullet)
        section.bullets = kept_sec

        for entry in section.entries:
            ctx = f"{section.title} / {entry.heading}"
            kept_entry: list[str] = []
            for bullet in entry.bullets:
                if is_aspirational_bullet(bullet):
                    archive_bullet(doc, tailor_target, f"{ctx} (Aspirational)", bullet)
                    stripped += 1
                else:
                    kept_entry.append(bullet)
            entry.bullets = kept_entry

            for sr in entry.sub_roles:
                ctx_sr = f"{ctx} / {sr.title}"
                kept_sr: list[str] = []
                for bullet in sr.bullets:
                    if is_aspirational_bullet(bullet):
                        archive_bullet(doc, tailor_target, f"{ctx_sr} (Aspirational)", bullet)
                        stripped += 1
                    else:
                        kept_sr.append(bullet)
                sr.bullets = kept_sr
    return stripped


def tailor_strict(
    doc: CVDocument,
    jd_text: str,
    *,
    tailor_target: str,
    target_title: str | None = None,
    pages: int = 2,
) -> tuple[CVDocument, list[str]]:
    """Return a tailored CVDocument and advisory warnings."""
    out = copy_document(doc)
    warnings: list[str] = []

    stripped = _strip_aspirational(out, tailor_target=tailor_target)
    if stripped:
        warnings.append(
            f"ASPIRATIONAL_STRIPPED: Removed {stripped} aspirational bullet(s) from renderable sections (archived in ## Facts)."
        )

    keywords = extract_keywords(jd_text)
    reorder_by_relevance(out, keywords)
    warnings.extend(prune_to_budget(out, keywords=keywords, pages=pages, tailor_target=tailor_target))

    fm = out.frontmatter
    if not fm.schema_version or fm.schema_version == "cv-md/1.0":
        fm.schema_version = CURRENT_SCHEMA
    fm.tailor_mode = "strict"
    fm.tailor_target = tailor_target
    if target_title:
        fm.headline = target_title

    if not any(w.startswith("SUMMARY") for w in warnings):
        warnings.append("SUMMARY_NOT_REWRITTEN: Strict CLI does not LLM-rewrite Summary; use skills/cv-tailor.")

    return out, warnings