"""CLI entry point for cvfmt: validate, render, init, linkedin, and from-url."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import yaml
from pydantic import ValidationError

from cvfmt import __version__
from cvfmt.linkedin import import_linkedin
from cvfmt.models import CVDocument
from cvfmt.parser import parse_cv_file, parse_cv_text
from cvfmt.renderer import compile_pdf
from cvfmt.typst_gen import normalize_hex_color
from cvfmt.url_import import LinkedInAuthwallError, import_from_url
from cvfmt.validator import validate_cv
from cvfmt.verifier import verify_pdf


app = typer.Typer(
    name="cvfmt",
    help="Validate and render cv-md/1.1 (and cv-md/1.0) Markdown CVs into clean, minimalist, ATS- and LLM-readable PDFs.",
    no_args_is_help=True,
)

STARTER_TEMPLATE = """---
schema: cv-md/1.1
name: Your Name
headline: Target Role Title
location: Amsterdam, Netherlands
work_authorization: EU Citizen
email: you@example.com
phone: "+31 6 0000 0000"
links:
  - label: LinkedIn
    url: https://linkedin.com/in/yourprofile
  - label: GitHub
    url: https://github.com/yourhandle
paper: a4
lang: en
---

## Summary

Concise 2–3 line summary highlighting years of experience, core domain, and primary strengths.

## Experience

### Senior Role — Company Name
*2023-01 – Present | Amsterdam, Netherlands (Hybrid)*

- Accomplished [X], as measured by [Y], by doing [Z].
- Led [scope/team/system], resulting in [concrete outcome].

## Skills

- **Core:** Skill A, Skill B, Skill C
- **Tools & Infrastructure:** Tool 1, Tool 2

## Education

### M.Sc. Field of Study — University Name
*2018-09 – 2020-06 | City, Country*

## Languages

- **English:** C2 (Proficient / Working Language)

## Facts

- **Preference: Notice Period** — 1 month; open to remote EU or hybrid roles.
- **Project: Example Side Project** — Stored here for future CV tailoring; never exported to PDF.
"""


def _print_validation(result) -> None:
    for issue in result.errors:
        loc = f" (line {issue.line})" if issue.line else ""
        typer.secho(f"ERROR [{issue.code}]{loc}: {issue.message}", fg=typer.colors.RED, err=True)
    for issue in result.warnings:
        loc = f" (line {issue.line})" if issue.line else ""
        typer.secho(f"WARN  [{issue.code}]{loc}: {issue.message}", fg=typer.colors.YELLOW, err=True)


def _load_cv_or_exit(path: Path) -> CVDocument:
    try:
        return parse_cv_file(path)
    except (yaml.YAMLError, ValidationError, ValueError, OSError) as exc:
        typer.secho(f"ERROR: Could not parse {path}: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


def _validate_render_options(
    paper: str | None, accent: str | None
) -> tuple[str | None, str | None]:
    normalized_paper: str | None = None
    if paper is not None:
        if paper.lower() not in ("a4", "letter"):
            typer.secho(
                f"ERROR: --paper must be 'a4' or 'letter' (got {paper!r}).",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        normalized_paper = paper.lower()

    normalized_accent: str | None = None
    if accent is not None:
        try:
            normalized_accent = normalize_hex_color(accent)
        except ValueError as exc:
            typer.secho(f"ERROR: {exc}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

    return normalized_paper, normalized_accent


def _compile_and_verify(
    doc: CVDocument,
    out_path: Path,
    *,
    paper: str | None,
    accent: str | None,
    verify: bool,
    strict: bool = False,
) -> None:
    try:
        compile_pdf(doc, out_path, paper_override=paper, accent_override=accent)
    except Exception as exc:
        typer.secho(f"ERROR: Typst compilation failed: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    typer.secho(f"Rendered: {out_path}", fg=typer.colors.GREEN)

    if verify:
        report = verify_pdf(doc, out_path)
        for err in report.errors:
            typer.secho(f"VERIFY ERROR: {err}", fg=typer.colors.RED, err=True)
        for warn in report.warnings:
            typer.secho(f"VERIFY WARN : {warn}", fg=typer.colors.YELLOW, err=True)

        if not report.ok or (strict and report.warnings):
            raise typer.Exit(code=2)

        typer.secho(
            f"Verified: {report.page_count} page(s), {report.link_count} clickable link(s), text layer clean.",
            fg=typer.colors.GREEN,
        )


@app.command()
def validate(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to cv-md/1.0 Markdown file."),
    allow_todos: bool = typer.Option(False, "--allow-todos", help="Allow [TODO] placeholders."),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors."),
) -> None:
    """Validate a cv-md/1.0 file against schema, ATS, and LLM rules."""
    doc = _load_cv_or_exit(path)
    result = validate_cv(doc, allow_todos=allow_todos)
    _print_validation(result)

    if not result.ok or (strict and result.warnings):
        raise typer.Exit(code=1)

    typer.secho(
        f"OK: {path} is valid {doc.frontmatter.schema_version} ({len(result.warnings)} warning(s)).",
        fg=typer.colors.GREEN,
    )


@app.command()
def render(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to cv-md/1.0 Markdown file."),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output PDF path (defaults to <stem>.pdf)."),
    paper: Optional[str] = typer.Option(None, "--paper", help="Override paper size: a4 or letter."),
    accent: Optional[str] = typer.Option(
        None,
        "--accent",
        help="Override accent color as 6-digit hex (default: #71717A light grey; e.g. '#0F766E' or '1A73E8').",
    ),
    allow_todos: bool = typer.Option(False, "--allow-todos", help="Allow rendering with [TODO] placeholders."),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors."),
    verify: bool = typer.Option(False, "--verify", help="Run PDF text-layer round-trip check after rendering."),
) -> None:
    """Validate and render a cv-md/1.0 file to a minimalist PDF."""
    norm_paper, norm_accent = _validate_render_options(paper, accent)
    doc = _load_cv_or_exit(path)
    result = validate_cv(doc, allow_todos=allow_todos)
    _print_validation(result)

    if not result.ok or (strict and result.warnings):
        raise typer.Exit(code=1)

    out_path = output or path.with_suffix(".pdf")
    _compile_and_verify(
        doc,
        out_path,
        paper=norm_paper,
        accent=norm_accent,
        verify=verify,
        strict=strict,
    )


@app.command()
def init(
    path: Path = typer.Argument(Path("cv.md"), help="Target path for starter cv-md/1.0 file."),
    force: bool = typer.Option(False, "--force", help="Overwrite if file exists."),
) -> None:
    """Scaffold a starter EU cv-md/1.0 Markdown file."""
    if path.exists() and not force:
        typer.secho(f"ERROR: {path} already exists. Pass --force to overwrite.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(STARTER_TEMPLATE, encoding="utf-8")
    typer.secho(f"Created starter CV: {path}", fg=typer.colors.GREEN)


@app.command()
def linkedin(
    source: Path = typer.Argument(
        ...,
        exists=True,
        help="LinkedIn 'Save to PDF' (.pdf), official Data Export (.zip), or CSV folder.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output .md path (or .pdf path when --pdf is set).",
    ),
    pdf: bool = typer.Option(
        False,
        "--pdf",
        help="Also render directly to a Warm Editorial PDF using cvfmt.",
    ),
    paper: str = typer.Option("a4", "--paper", help="Paper size: a4 (default) or letter."),
    accent: Optional[str] = typer.Option(
        None,
        "--accent",
        help="Optional 6-digit hex accent color for --pdf (default: #71717A light grey).",
    ),
    verify: bool = typer.Option(
        False,
        "--verify",
        help="Run PDF text-layer verification when --pdf is set.",
    ),
) -> None:
    """Import a LinkedIn profile export (.pdf, .zip, or CSV folder) into cv-md/1.0 (and optionally PDF)."""
    norm_paper, norm_accent = _validate_render_options(paper, accent)
    assert norm_paper is not None

    try:
        md_text = import_linkedin(source, paper=norm_paper)
    except Exception as exc:
        typer.secho(f"ERROR: Failed to import LinkedIn export: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if pdf:
        if output is not None:
            pdf_out = output if output.suffix.lower() == ".pdf" else output.with_suffix(".pdf")
        elif source.suffix.lower() == ".pdf":
            pdf_out = source.with_name(f"{source.stem}-cv.pdf")
        else:
            pdf_out = source.with_suffix(".pdf")
        if source.is_file() and pdf_out.resolve() == source.resolve():
            typer.secho(
                f"ERROR: Refusing to overwrite input file {source}. Specify a different -o path.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        md_out = pdf_out.with_suffix(".md")
    else:
        md_out = output or source.with_suffix(".md")
        pdf_out = None

    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(md_text, encoding="utf-8")
    typer.secho(f"Imported LinkedIn -> {md_out}", fg=typer.colors.GREEN)

    doc = parse_cv_text(md_text, source_path=str(md_out))
    val = validate_cv(doc, allow_todos=True)
    _print_validation(val)

    if pdf and pdf_out is not None:
        if not val.ok:
            typer.secho(
                "ERROR: Imported CV has schema errors; fix them before rendering PDF.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        _compile_and_verify(
            doc,
            pdf_out,
            paper=norm_paper,
            accent=norm_accent,
            verify=verify,
        )


@app.command("from-url")
def from_url(
    url: str = typer.Argument(
        ...,
        help="Public CV URL (HTML CV page, JSON Resume .json, or raw cv-md/1.0 Markdown).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output .md path (or .pdf path when --pdf is set). Defaults to cv-imported.md / .pdf.",
    ),
    pdf: bool = typer.Option(
        False,
        "--pdf",
        help="Also render directly to a Warm Editorial PDF using cvfmt.",
    ),
    paper: str = typer.Option("a4", "--paper", help="Paper size: a4 (default) or letter."),
    accent: Optional[str] = typer.Option(
        None,
        "--accent",
        help="Optional 6-digit hex accent color for --pdf (default: #71717A light grey).",
    ),
    verify: bool = typer.Option(
        False,
        "--verify",
        help="Run PDF text-layer verification when --pdf is set.",
    ),
) -> None:
    """Import a public CV webpage, JSON Resume URL, or raw cv-md/1.0 URL into cv-md/1.0 (and optionally PDF)."""
    norm_paper, norm_accent = _validate_render_options(paper, accent)
    assert norm_paper is not None

    try:
        md_text = import_from_url(url, paper=norm_paper)
    except LinkedInAuthwallError as exc:
        typer.secho(f"NOTICE: {exc}", fg=typer.colors.YELLOW, err=True)
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"ERROR: Failed to import URL: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    base = output or Path("cv-imported.pdf" if pdf else "cv-imported.md")
    if pdf:
        pdf_out = base if base.suffix.lower() == ".pdf" else base.with_suffix(".pdf")
        md_out = pdf_out.with_suffix(".md")
    else:
        md_out = base
        pdf_out = None

    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(md_text, encoding="utf-8")
    typer.secho(f"Imported URL -> {md_out}", fg=typer.colors.GREEN)

    doc = parse_cv_text(md_text, source_path=str(md_out))
    val = validate_cv(doc, allow_todos=True)
    _print_validation(val)

    if pdf and pdf_out is not None:
        if not val.ok:
            typer.secho(
                "ERROR: Imported CV has schema errors; fix them before rendering PDF.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        _compile_and_verify(
            doc,
            pdf_out,
            paper=norm_paper,
            accent=norm_accent,
            verify=verify,
        )


@app.command()
def version() -> None:
    """Print cvfmt version."""
    typer.echo(f"cvfmt {__version__}")


if __name__ == "__main__":
    app()
