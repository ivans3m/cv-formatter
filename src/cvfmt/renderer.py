"""Typst compilation wrapper with bundled IBM Plex Sans and Tagged PDF (PDF/UA-1)."""

from __future__ import annotations

from pathlib import Path

import typst

from cvfmt.models import CVDocument
from cvfmt.typst_gen import generate_typst


FONTS_DIR = Path(__file__).resolve().parent / "fonts"


def _compile_typst(typst_source: str, **kwargs):
    """Compile Typst source with bundled IBM Plex Sans, falling back to system fonts only on missing glyphs."""
    data = typst_source.encode("utf-8")
    try:
        return typst.compile(
            data,
            font_paths=[str(FONTS_DIR)],
            ignore_system_fonts=True,
            **kwargs,
        )
    except typst.TypstError as exc:
        if "could not be displayed with font" not in str(exc):
            raise
        return typst.compile(
            data,
            font_paths=[str(FONTS_DIR)],
            ignore_system_fonts=False,
            **kwargs,
        )


def compile_pdf(
    doc: CVDocument,
    output_path: str | Path,
    *,
    paper_override: str | None = None,
    accent_override: str | None = None,
    include_aspirational: bool = False,
    pdf_ua: bool = True,
) -> Path:
    """Compile a CVDocument into a minimalist, tagged PDF using bundled IBM Plex Sans."""
    typst_source = generate_typst(
        doc,
        paper_override=paper_override,
        accent_override=accent_override,
        include_aspirational=include_aspirational,
    )
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    standards = ["ua-1"] if pdf_ua else []
    pdf_bytes = _compile_typst(
        typst_source,
        pdf_tags=True,
        pdf_standards=standards,
    )
    out.write_bytes(pdf_bytes)
    return out


def compile_pngs(
    doc: CVDocument,
    output_dir: str | Path,
    *,
    stem: str = "page",
    paper_override: str | None = None,
    accent_override: str | None = None,
    include_aspirational: bool = False,
    ppi: float = 144.0,
) -> list[Path]:
    """Render a CVDocument to PNG pages for visual review."""
    typst_source = generate_typst(
        doc,
        paper_override=paper_override,
        accent_override=accent_override,
        include_aspirational=include_aspirational,
    )
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result = _compile_typst(
        typst_source,
        format="png",
        ppi=ppi,
    )
    pages = result if isinstance(result, list) else [result]
    written: list[Path] = []
    for idx, page_bytes in enumerate(pages, start=1):
        p = out_dir / f"{stem}-p{idx}.png"
        p.write_bytes(page_bytes)
        written.append(p)
    return written
