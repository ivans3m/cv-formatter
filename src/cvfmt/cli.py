"""CLI entry point for cvfmt: validate, render, and init cv-md/1.0 CVs."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from cvfmt import __version__
from cvfmt.parser import parse_cv_file
from cvfmt.renderer import compile_pdf
from cvfmt.validator import validate_cv
from cvfmt.verifier import verify_pdf


app = typer.Typer(
    name="cvfmt",
    help="Validate and render cv-md/1.0 Markdown CVs into clean, minimalist, ATS- and LLM-readable PDFs.",
    no_args_is_help=True,
)

STARTER_TEMPLATE = """---
schema: cv-md/1.0
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
"""


def _print_validation(result) -> None:
    for issue in result.errors:
        loc = f" (line {issue.line})" if issue.line else ""
        typer.secho(f"ERROR [{issue.code}]{loc}: {issue.message}", fg=typer.colors.RED, err=True)
    for issue in result.warnings:
        loc = f" (line {issue.line})" if issue.line else ""
        typer.secho(f"WARN  [{issue.code}]{loc}: {issue.message}", fg=typer.colors.YELLOW, err=True)


@app.command()
def validate(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to cv-md/1.0 Markdown file."),
    allow_todos: bool = typer.Option(False, "--allow-todos", help="Allow [TODO] placeholders."),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors."),
) -> None:
    """Validate a cv-md/1.0 file against schema, ATS, and LLM rules."""
    doc = parse_cv_file(path)
    result = validate_cv(doc, allow_todos=allow_todos)
    _print_validation(result)

    if not result.ok or (strict and result.warnings):
        raise typer.Exit(code=1)

    typer.secho(
        f"OK: {path} is valid cv-md/1.0 ({len(result.warnings)} warning(s)).",
        fg=typer.colors.GREEN,
    )


@app.command()
def render(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to cv-md/1.0 Markdown file."),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output PDF path (defaults to <stem>.pdf)."),
    paper: Optional[str] = typer.Option(None, "--paper", help="Override paper size: a4 or letter."),
    allow_todos: bool = typer.Option(False, "--allow-todos", help="Allow rendering with [TODO] placeholders."),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors."),
    verify: bool = typer.Option(False, "--verify", help="Run PDF text-layer round-trip check after rendering."),
) -> None:
    """Validate and render a cv-md/1.0 file to a minimalist PDF."""
    if paper is not None and paper.lower() not in ("a4", "letter"):
        typer.secho(f"ERROR: --paper must be 'a4' or 'letter' (got {paper!r}).", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    doc = parse_cv_file(path)
    result = validate_cv(doc, allow_todos=allow_todos)
    _print_validation(result)

    if not result.ok or (strict and result.warnings):
        raise typer.Exit(code=1)

    out_path = output or path.with_suffix(".pdf")
    try:
        compile_pdf(doc, out_path, paper_override=paper)
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
def version() -> None:
    """Print cvfmt version."""
    typer.echo(f"cvfmt {__version__}")


if __name__ == "__main__":
    app()
