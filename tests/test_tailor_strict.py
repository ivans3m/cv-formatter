"""Strict tailoring CLI and pipeline tests."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from cvfmt.cli import app
from cvfmt.parser import parse_cv_text
from cvfmt.tailor import tailor_strict
from cvfmt.validator import validate_cv

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def test_tailor_strict_reorders_and_validates() -> None:
    from cvfmt.parser import parse_cv_file

    jd = (FIXTURES_DIR / "jd-backend-sample.txt").read_text(encoding="utf-8")
    base = parse_cv_file(FIXTURES_DIR / "senior-eu-2page.md")
    tailored, _ = tailor_strict(base, jd, tailor_target="Senior Backend", pages=2)
    val = validate_cv(tailored)
    assert val.ok, val.errors
    assert tailored.frontmatter.tailor_mode == "strict"
    assert tailored.frontmatter.tailor_target == "Senior Backend"

    exp = next(s for s in tailored.sections if s.title.lower() == "experience")
    assert exp.entries[0].heading.startswith("Acme Payments")


def test_tailor_cli_smoke(tmp_path: Path) -> None:
    out = tmp_path / "tailored.md"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "tailor",
            str(FIXTURES_DIR / "jd-backend-sample.txt"),
            "--base",
            str(FIXTURES_DIR / "senior-eu-2page.md"),
            "-o",
            str(out),
            "--mode",
            "strict",
            "--target-title",
            "Senior Backend Engineer",
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    doc = parse_cv_text(out.read_text(encoding="utf-8"))
    assert doc.frontmatter.headline == "Senior Backend Engineer"
    assert validate_cv(doc).ok


def test_dreamer_prepare_bundle(tmp_path: Path) -> None:
    runner = CliRunner()
    bundle = tmp_path / "bundle"
    result = runner.invoke(
        app,
        [
            "tailor",
            str(FIXTURES_DIR / "jd-backend-sample.txt"),
            "--base",
            str(FIXTURES_DIR / "senior-eu-2page.md"),
            "--mode",
            "dreamer",
            "--prepare",
            str(bundle),
        ],
    )
    assert result.exit_code == 0, result.output
    assert (bundle / "jd.txt").exists()
    assert (bundle / "base.md").exists()
    assert (bundle / "prompt.md").exists()


def test_tailor_strict_strips_aspirational_and_archives_under_heading() -> None:
    md = """---
schema: cv-md/1.1
name: Alex Dev
email: alex@example.com
tailor_mode: dreamer
---

## Experience

### Engineer — Acme
*2023-01 – Present | Berlin, Germany*

- Built Go microservices with PostgreSQL and Kafka.
- **(Aspirational)** Scaled platform to 10M users.
- **(aspirational)** Managed 50-person engineering org.

## Skills

- **Core:** Go, PostgreSQL, Kafka

## Languages

- **English:** C2
"""
    base = parse_cv_text(md)
    tailored, warnings = tailor_strict(base, "Go PostgreSQL Kafka backend", tailor_target="Backend @ Acme", pages=2)
    val = validate_cv(tailored)
    assert val.ok, val.errors
    assert any(w.startswith("ASPIRATIONAL_STRIPPED:") for w in warnings)

    exp = next(s for s in tailored.sections if s.title.lower() == "experience")
    assert len(exp.entries[0].bullets) == 1
    assert "Go microservices" in exp.entries[0].bullets[0]

    facts = tailored.facts_section
    assert facts is not None
    archive = next(e for e in facts.entries if e.heading == "Archived for Backend @ Acme")
    assert len(archive.bullets) == 2


def test_tailor_budget_counts_entry_paragraphs_and_prunes_section_bullets() -> None:
    long_para = "Context paragraph about architecture. " * 90  # ~3420 chars (> 3200 1-page budget)
    md = f"""---
schema: cv-md/1.1
name: Alex Dev
email: alex@example.com
---

## Experience

- General consulting unrelated to target.
- Go Kafka distributed systems consulting.

### Engineer — Acme
*2023-01 – Present | Berlin, Germany*

{long_para}

- Built Go Kafka settlement service.

## Projects

- Unrelated hobby script.
- Built Go PostgreSQL benchmarking tool.

## Skills

- **Core:** Go, Kafka, PostgreSQL

## Languages

- **English:** C2
"""
    base = parse_cv_text(md)
    tailored, _ = tailor_strict(base, "Go Kafka PostgreSQL backend", tailor_target="Backend Role", pages=1)
    assert validate_cv(tailored).ok

    exp = next(s for s in tailored.sections if s.title.lower() == "experience")
    proj = next(s for s in tailored.sections if s.title.lower() == "projects")
    # Section-level bullets were pruned under the 1-page budget because entry.paragraphs pushed total over 3200
    facts = tailored.facts_section
    assert facts is not None
    archive = next(e for e in facts.entries if e.heading == "Archived for Backend Role")
    assert len(archive.bullets) > 0
    assert len(exp.bullets) == 0
    assert len(proj.bullets) == 0


def test_tailor_cli_output_extension_and_dreamer_pdf_guards(tmp_path: Path) -> None:
    runner = CliRunner()
    jd_path = str(FIXTURES_DIR / "jd-backend-sample.txt")
    base_path = str(FIXTURES_DIR / "senior-eu-2page.md")

    # Non-.md output without --pdf is rejected
    bad_no_pdf = runner.invoke(
        app,
        ["tailor", jd_path, "--base", base_path, "-o", str(tmp_path / "out.pdf"), "--mode", "strict"],
    )
    assert bad_no_pdf.exit_code == 1

    # .pdf output with --pdf writes sibling .md and .pdf without overwriting markdown
    pdf_target = tmp_path / "tailored.pdf"
    ok_pdf = runner.invoke(
        app,
        ["tailor", jd_path, "--base", base_path, "-o", str(pdf_target), "--mode", "strict", "--pdf"],
    )
    assert ok_pdf.exit_code == 0, ok_pdf.output
    assert pdf_target.exists()
    assert pdf_target.read_bytes().startswith(b"%PDF")
    md_sibling = tmp_path / "tailored.md"
    assert md_sibling.exists()
    assert md_sibling.read_text(encoding="utf-8").startswith("---\n")

    # --mode dreamer --pdf errors explicitly
    bad_dreamer_pdf = runner.invoke(
        app,
        ["tailor", jd_path, "--base", base_path, "--mode", "dreamer", "--pdf"],
    )
    assert bad_dreamer_pdf.exit_code == 1

    # Braces in --target-title work with --prepare
    bundle = tmp_path / "bundle-braces"
    ok_braces = runner.invoke(
        app,
        [
            "tailor",
            jd_path,
            "--base",
            base_path,
            "--mode",
            "dreamer",
            "--prepare",
            str(bundle),
            "--target-title",
            "Backend {Go/Python}",
        ],
    )
    assert ok_braces.exit_code == 0, ok_braces.output
    assert "Backend {Go/Python}" in (bundle / "prompt.md").read_text(encoding="utf-8")