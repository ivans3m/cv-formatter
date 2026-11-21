"""Typst compilation wrapper with bundled IBM Plex Sans and Tagged PDF (PDF/UA-1)."""

from __future__ import annotations

from pathlib import Path

import typst

from cvfmt.models import CVDocument
from cvfmt.typst_gen import generate_typst


FONTS_DIR = Path(__file__).resolve().parent / "fonts"


def compile_pdf(
    doc: CVDocument,
    output_path: str | Path,
    *,
    paper_override: str | None = None,
    pdf_ua: bool = True,
) -> Path:
    """Compile a CVDocument into a minimalist, tagged PDF using bundled IBM Plex Sans."""
    typst_source = generate_typst(doc, paper_override=paper_override)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    standards = ["ua-1"] if pdf_ua else []
    pdf_bytes = typst.compile(
        typst_source.encode("utf-8"),
        font_paths=[str(FONTS_DIR)],
        ignore_system_fonts=True,
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
    ppi: float = 144.0,
) -> list[Path]:
    """Render a CVDocument to PNG pages for visual review."""
    typst_source = generate_typst(doc, paper_override=paper_override)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result = typst.compile(
        typst_source.encode("utf-8"),
        font_paths=[str(FONTS_DIR)],
        ignore_system_fonts=True,
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
