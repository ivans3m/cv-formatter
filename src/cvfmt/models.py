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
    "Awards",
    "Speaking",
    "Publications",
    "Volunteering",
    "Courses",
    "Interests",
    "Facts",
)

NON_RENDERED_SECTIONS: frozenset[str] = frozenset({"facts"})

CANONICAL_SECTIONS_LOWER: dict[str, str] = {s.lower(): s for s in CANONICAL_SECTIONS}

# Localized EU canonical heading aliases (nl, de, fr) mapped to canonical lowercase keys
LOCALIZED_SECTION_ALIASES: dict[str, str] = {
    # English canonical
    **{s.lower(): s.lower() for s in CANONICAL_SECTIONS},
    # Dutch (nl)
    "profiel": "summary",
    "samenvatting": "summary",
    "over mij": "summary",
    "werkervaring": "experience",
    "ervaring": "experience",
    "projecten": "projects",
    "vaardigheden": "skills",
    "competenties": "skills",
    "opleiding": "education",
    "opleidingen": "education",
    "talen": "languages",
    "certificeringen": "certifications",
    "certificaten": "certifications",
    "prijzen": "awards",
    "onderscheidingen": "awards",
    "prijzen & onderscheidingen": "awards",
    "lezingen": "speaking",
    "sprekerservaring": "speaking",
    "presentaties": "speaking",
    "publicaties": "publications",
    "vrijwilligerswerk": "volunteering",
    "cursussen": "courses",
    "trainingen": "courses",
    "interesses": "interests",
    "hobby's": "interests",
    "feiten": "facts",
    # German (de)
    "profil": "summary",
    "zusammenfassung": "summary",
    "kurzprofil": "summary",
    "über mich": "summary",
    "berufserfahrung": "experience",
    "erfahrung": "experience",
    "projekte": "projects",
    "kenntnisse": "skills",
    "fähigkeiten": "skills",
    "kompetenzen": "skills",
    "ausbildung": "education",
    "bildung": "education",
    "studium": "education",
    "sprachen": "languages",
    "sprachkenntnisse": "languages",
    "zertifizierungen": "certifications",
    "zertifikate": "certifications",
    "auszeichnungen": "awards",
    "preise": "awards",
    "vorträge": "speaking",
    "publikationen": "publications",
    "veröffentlichungen": "publications",
    "ehrenamt": "volunteering",
    "engagement": "volunteering",
    "kurse": "courses",
    "weiterbildung": "courses",
    "fortbildungen": "courses",
    "interessen": "interests",
    "hobbys": "interests",
    "fakten": "facts",
    # French (fr)
    "résumé": "summary",
    "à propos": "summary",
    "expérience": "experience",
    "expérience professionnelle": "experience",
    "expériences": "experience",
    "expériences professionnelles": "experience",
    "projets": "projects",
    "compétences": "skills",
    "formation": "education",
    "formations": "education",
    "éducation": "education",
    "langues": "languages",
    "certificats": "certifications",
    "prix": "awards",
    "distinctions": "awards",
    "prix et distinctions": "awards",
    "conférences": "speaking",
    "interventions": "speaking",
    "bénévolat": "volunteering",
    "cours": "courses",
    "formations complémentaires": "courses",
    "centres d'intérêt": "interests",
    "intérêts": "interests",
    "faits": "facts",
}


def canonical_section_key(title: str) -> str | None:
    """Resolve an English or localized (nl/de/fr) section heading to its canonical lowercase key."""
    normalized = " ".join(
        title.replace("\u2019", "'").replace("\u2018", "'").strip().lower().split()
    )
    return LOCALIZED_SECTION_ALIASES.get(normalized)


class LinkItem(BaseModel):
    label: str
    url: str


ASPIRATIONAL_PREFIX = "**(Aspirational)** "
_ASPIRATIONAL_MARKER_LOWER = ASPIRATIONAL_PREFIX.strip().lower()


def is_aspirational_bullet(text: str) -> bool:
    """True when a renderable bullet is marked as dreamer/aspirational content."""
    return text.strip().lower().startswith(_ASPIRATIONAL_MARKER_LOWER)


class Frontmatter(BaseModel):
    schema_version: str = Field(default="", alias="schema")
    name: str = ""
    headline: str | None = None
    location: str | None = None
    work_authorization: str | None = None
    availability: str | None = None
    email: str = ""
    phone: str | None = None
    links: list[LinkItem] = Field(default_factory=list)
    paper: str = "a4"
    lang: str = "en"
    accent: str | None = None
    tailor_mode: Literal["strict", "dreamer"] | None = None
    tailor_target: str | None = None

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
        return [s for s in self.sections if canonical_section_key(s.title) not in NON_RENDERED_SECTIONS]

    @property
    def facts_section(self) -> Section | None:
        """Optional non-exported '## Facts' memory bank section, if present."""
        return next((s for s in self.sections if canonical_section_key(s.title) == "facts"), None)


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
