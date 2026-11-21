"""Unit and round-trip integration tests for cvfmt."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from cvfmt.cli import app
from cvfmt.parser import parse_cv_file, parse_cv_text
from cvfmt.renderer import compile_pdf, compile_pngs
from cvfmt.validator import validate_cv
from cvfmt.verifier import verify_pdf


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
GOLDEN_FIXTURES = [
    ("junior-eu-1page.md", 1),
    ("senior-eu-2page.md", 2),
    ("consultant-multirole.md", 1),
    ("diacritics-stress.md", 1),
]


@pytest.mark.parametrize("filename,expected_max_pages", GOLDEN_FIXTURES)
def test_golden_fixtures_validate_render_and_verify(
    filename: str, expected_max_pages: int, tmp_path: Path
) -> None:
    md_path = FIXTURES_DIR / filename
    doc = parse_cv_file(md_path)

    val = validate_cv(doc)
    assert val.ok, f"Unexpected validation errors for {filename}: {val.errors}"

    pdf_path = tmp_path / f"{md_path.stem}.pdf"
    compile_pdf(doc, pdf_path)
    assert pdf_path.exists() and pdf_path.stat().st_size > 1000

    report = verify_pdf(doc, pdf_path)
    assert report.ok, f"PDF verification failed for {filename}: {report.errors}"
    assert 1 <= report.page_count <= expected_max_pages, (
        f"{filename}: expected <= {expected_max_pages} page(s), got {report.page_count}"
    )


def test_diacritics_and_ligatures_exact_roundtrip(tmp_path: Path) -> None:
    md_path = FIXTURES_DIR / "diacritics-stress.md"
    doc = parse_cv_file(md_path)
    pdf_path = tmp_path / "diacritics.pdf"
    compile_pdf(doc, pdf_path)

    report = verify_pdf(doc, pdf_path)
    assert report.ok, report.errors

    for token in (
        "Łukasz",
        "Żółć-François",
        "Zürich",
        "München",
        "Kraków",
        "Malmö",
        "Łódź",
        "Gdańsk",
        "Straße",
        "€1.2M",
        "offline-first",
        "profiling",
        "workflow",
        "efficient",
        "file-export",
    ):
        assert token in report.extracted_text, f"Token {token!r} missing or corrupted in PDF text"


def test_letter_paper_override_compiles(tmp_path: Path) -> None:
    doc = parse_cv_file(FIXTURES_DIR / "junior-eu-1page.md")
    pdf_path = tmp_path / "junior-letter.pdf"
    compile_pdf(doc, pdf_path, paper_override="letter")
    report = verify_pdf(doc, pdf_path)
    assert report.ok, report.errors


def test_png_preview_generation(tmp_path: Path) -> None:
    doc = parse_cv_file(FIXTURES_DIR / "senior-eu-2page.md")
    pngs = compile_pngs(doc, tmp_path, stem="senior")
    assert len(pngs) == 2
    for p in pngs:
        assert p.exists() and p.stat().st_size > 5000


def test_validator_catches_hard_errors() -> None:
    bad_md = """---
schema: wrong/0.1
name: ""
email: not-an-email
paper: tabloid
---

## My Journey

### Engineer — Acme
*April 2023 - now | Berlin*

- [TODO: add metric]
"""
    doc = parse_cv_text(bad_md)
    res = validate_cv(doc)
    error_codes = {i.code for i in res.errors}
    warn_codes = {i.code for i in res.warnings}

    assert not res.ok
    assert "SCHEMA_VERSION" in error_codes
    assert "MISSING_NAME" in error_codes
    assert "INVALID_EMAIL" in error_codes
    assert "INVALID_PAPER" in error_codes
    assert "MISSING_EXPERIENCE" in error_codes
    assert "INVALID_DATE" in error_codes
    assert "UNRESOLVED_TODO" in error_codes
    assert "NON_CANONICAL_SECTION" in warn_codes
    assert "MISSING_LANGUAGES" in warn_codes


def test_validator_allow_todos_flag() -> None:
    md = """---
schema: cv-md/1.0
name: Alex Dev
email: alex@example.com
---

## Experience

### Engineer — Acme
*2023-01 – Present | Berlin, Germany*

- Built service [TODO: add throughput].

## Languages

- **English:** C2
"""
    doc = parse_cv_text(md)
    assert not validate_cv(doc, allow_todos=False).ok
    assert validate_cv(doc, allow_todos=True).ok


def test_cli_init_validate_and_render(tmp_path: Path) -> None:
    runner = CliRunner()
    cv_path = tmp_path / "starter.md"

    res_init = runner.invoke(app, ["init", str(cv_path)])
    assert res_init.exit_code == 0, res_init.output
    assert cv_path.exists()

    res_val = runner.invoke(app, ["validate", str(cv_path)])
    assert res_val.exit_code == 0, res_val.output

    pdf_path = tmp_path / "starter.pdf"
    res_render = runner.invoke(app, ["render", str(cv_path), "-o", str(pdf_path), "--verify"])
    assert res_render.exit_code == 0, res_render.output
    assert pdf_path.exists()

    pdf_accent = tmp_path / "starter-teal.pdf"
    res_accent = runner.invoke(
        app, ["render", str(cv_path), "-o", str(pdf_accent), "--accent", "0F766E", "--verify"]
    )
    assert res_accent.exit_code == 0, res_accent.output
    assert pdf_accent.exists()

    res_bad_accent = runner.invoke(
        app, ["render", str(cv_path), "--accent", "not-a-hex"]
    )
    assert res_bad_accent.exit_code == 1


def test_entry_heading_prefers_em_dash_over_en_dash() -> None:
    md = """---
schema: cv-md/1.0
name: Test User
email: test@example.com
---

## Experience

### Earlier Roles (2003 – 2009) — Acme & Beta
*2003 – 2009 | Kyiv, Ukraine*

- Led digital projects.
"""
    doc = parse_cv_text(md)
    entry = doc.sections[0].entries[0]
    assert entry.primary == "Earlier Roles (2003 – 2009)"
    assert entry.secondary == "Acme & Beta"
