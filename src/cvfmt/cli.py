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
from cvfmt.tailor import coverage_report, tailor_strict, write_prepare_bundle
from cvfmt.validator import validate_cv
from cvfmt.verifier import verify_pdf
from cvfmt.writer import document_to_markdown


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
    allow_aspirational: bool = False,
) -> None:
    try:
        compile_pdf(
            doc,
            out_path,
            paper_override=paper,
            accent_override=accent,
            include_aspirational=allow_aspirational,
        )
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
    allow_aspirational: bool = typer.Option(
        False,
        "--allow-aspirational",
        help="Allow **(Aspirational)** bullets in dreamer-tailored CVs.",
    ),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors."),
) -> None:
    """Validate a cv-md/1.0 file against schema, ATS, and LLM rules."""
    doc = _load_cv_or_exit(path)
    result = validate_cv(doc, allow_todos=allow_todos, allow_aspirational=allow_aspirational)
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
    allow_aspirational: bool = typer.Option(
        False,
        "--allow-aspirational",
        help="Include **(Aspirational)** dreamer bullets in the PDF (gap-analysis only).",
    ),
    strict: bool = typer.Option(False, "--strict", help="Treat warnings as errors."),
    verify: bool = typer.Option(False, "--verify", help="Run PDF text-layer round-trip check after rendering."),
) -> None:
    """Validate and render a cv-md/1.0 file to a minimalist PDF."""
    norm_paper, norm_accent = _validate_render_options(paper, accent)
    doc = _load_cv_or_exit(path)
    result = validate_cv(doc, allow_todos=allow_todos, allow_aspirational=allow_aspirational)
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
        allow_aspirational=allow_aspirational,
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
def tailor(
    job: Path = typer.Argument(..., exists=True, readable=True, help="Job description text file."),
    base: Path = typer.Option(..., "--base", exists=True, readable=True, help="Master cv-md file."),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output tailored .md path (required for --mode strict).",
    ),
    mode: str = typer.Option(
        "strict",
        "--mode",
        help="strict: deterministic reorder/trim; dreamer: coverage report or --prepare bundle.",
    ),
    target_title: Optional[str] = typer.Option(
        None,
        "--target-title",
        help="Override frontmatter headline for the target role (strict mode).",
    ),
    pages: int = typer.Option(2, "--pages", min=1, max=2, help="Soft page budget (1 or 2)."),
    prepare: Optional[Path] = typer.Option(
        None,
        "--prepare",
        help="Write dreamer LLM bundle (jd.txt, base.md, prompt.md) to this directory.",
    ),
    pdf: bool = typer.Option(False, "--pdf", help="Render tailored output to PDF (strict with -o)."),
    paper: str = typer.Option("a4", "--paper", help="Paper size when --pdf is set."),
    accent: Optional[str] = typer.Option(None, "--accent", help="Hex accent when --pdf is set."),
    verify: bool = typer.Option(False, "--verify", help="Verify PDF when --pdf is set."),
    allow_aspirational: bool = typer.Option(
        False,
        "--allow-aspirational",
        help="Pass through to validate/render for dreamer artifacts.",
    ),
) -> None:
    """Tailor a master cv-md CV against a job description (strict deterministic or dreamer prep)."""
    mode_norm = mode.strip().lower()
    if mode_norm not in ("strict", "dreamer"):
        typer.secho("ERROR: --mode must be 'strict' or 'dreamer'.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    jd_text = job.read_text(encoding="utf-8")
    doc = _load_cv_or_exit(base)
    target = target_title or job.stem.replace("_", " ").replace("-", " ")

    if mode_norm == "dreamer":
        if pdf:
            typer.secho(
                "ERROR: --pdf is not supported with --mode dreamer. "
                "Generate a dreamer CV first (using --prepare or skills/cv-tailor), "
                "then run 'cvfmt render <file.md> --allow-aspirational'.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        if output is not None:
            typer.secho(
                "ERROR: --mode dreamer does not write tailored Markdown without an LLM. "
                "Use --prepare DIR or skills/cv-tailor.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        typer.echo(coverage_report(doc, jd_text))
        if prepare is not None:
            write_prepare_bundle(doc, jd_text, prepare, tailor_target=target)
            typer.secho(f"Prepared dreamer bundle: {prepare}", fg=typer.colors.GREEN)
        return

    if output is None:
        typer.secho("ERROR: --mode strict requires -o/--output for the tailored .md path.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    suffix = output.suffix.lower()
    if pdf:
        if suffix not in (".md", ".pdf"):
            typer.secho(
                f"ERROR: -o/--output must be a .md or .pdf path when --pdf is set (got {output}).",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        norm_paper, norm_accent = _validate_render_options(paper, accent)
        pdf_out = output if suffix == ".pdf" else output.with_suffix(".pdf")
        md_out = pdf_out.with_suffix(".md")
    else:
        if suffix != ".md":
            typer.secho(
                f"ERROR: -o/--output must be a .md path when --pdf is not set (got {output}). "
                "Pass --pdf to also render a PDF.",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        norm_paper, norm_accent = None, None
        md_out = output
        pdf_out = None

    tailored, advisories = tailor_strict(
        doc,
        jd_text,
        tailor_target=target,
        target_title=target_title,
        pages=pages,
    )
    for note in advisories:
        typer.secho(f"NOTE: {note}", fg=typer.colors.YELLOW, err=True)

    md_text = document_to_markdown(tailored)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(md_text, encoding="utf-8")
    typer.secho(f"Tailored (strict) -> {md_out}", fg=typer.colors.GREEN)

    parsed = parse_cv_text(md_text, source_path=str(md_out))
    val = validate_cv(parsed, allow_aspirational=allow_aspirational)
    _print_validation(val)
    if not val.ok:
        raise typer.Exit(code=1)

    if pdf and pdf_out is not None:
        _compile_and_verify(
            parsed,
            pdf_out,
            paper=norm_paper,
            accent=norm_accent,
            verify=verify,
            allow_aspirational=allow_aspirational,
        )


@app.command()
def version() -> None:
    """Print cvfmt version."""
    typer.echo(f"cvfmt {__version__}")


if __name__ == "__main__":
    app()
