"""Data models for cv-md/1.1 (and backward-compatible cv-md/1.0) documents and validation diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field


CURRENT_SCHEMA: str = "cv-md/1.1"
SUPPORTED_SCHEMAS: tuple[str, ...] = ("cv-md/1.0", "cv-md/1.1")

CANONICAL_SECTIONS: tuple[str, ...] = (
    "Summary",
    "Experience",
    "Projects",
    "Skills",
    "Education",
    "Languages",
    "Certifications",
    "Publications",
    "Facts",
)

NON_RENDERED_SECTIONS: frozenset[str] = frozenset({"facts"})

CANONICAL_SECTIONS_LOWER: dict[str, str] = {s.lower(): s for s in CANONICAL_SECTIONS}


class LinkItem(BaseModel):
    label: str
    url: str


class Frontmatter(BaseModel):
    schema_version: str = Field(default="", alias="schema")
    name: str = ""
    headline: str | None = None
    location: str | None = None
    work_authorization: str | None = None
    email: str = ""
    phone: str | None = None
    links: list[LinkItem] = Field(default_factory=list)
    paper: str = "a4"
    lang: str = "en"
    accent: str | None = None

    model_config = {"populate_by_name": True}


@dataclass
class SubRole:
    title: str
    date_range: str | None = None
    bullets: list[str] = field(default_factory=list)
    line: int = 0


@dataclass
class Entry:
    heading: str
    primary: str
    secondary: str | None = None
    date_range: str | None = None
    location: str | None = None
    raw_meta: str | None = None
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    sub_roles: list[SubRole] = field(default_factory=list)
    line: int = 0


@dataclass
class Section:
    title: str
    paragraphs: list[str] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)
    line: int = 0
    end_line: int = 0


@dataclass
class CVDocument:
    frontmatter: Frontmatter
    sections: list[Section] = field(default_factory=list)
    raw_frontmatter: dict = field(default_factory=dict)
    raw_body: str = ""
    body_start_line: int = 1
    source_path: str | None = None

    @property
    def renderable_sections(self) -> list[Section]:
        """Sections exported to PDF (excludes non-rendered sections such as '## Facts')."""
        return [s for s in self.sections if s.title.lower() not in NON_RENDERED_SECTIONS]

    @property
    def facts_section(self) -> Section | None:
        """Optional non-exported '## Facts' memory bank section, if present."""
        return next((s for s in self.sections if s.title.lower() == "facts"), None)


@dataclass
class ValidationIssue:
    severity: Literal["error", "warning"]
    code: str
    message: str
    line: int | None = None


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0
