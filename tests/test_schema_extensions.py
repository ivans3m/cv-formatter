"""Tests for cv-md/1.1 schema extensions: optional blocks, availability, patterns, and EU localization."""

from __future__ import annotations

import zipfile
from pathlib import Path

from cvfmt.linkedin import import_linkedin
from cvfmt.parser import parse_cv_text
from cvfmt.renderer import compile_pdf
from cvfmt.tailor import tailor_strict
from cvfmt.url_import import convert_json_resume
from cvfmt.validator import validate_cv
from cvfmt.verifier import verify_pdf
from cvfmt.writer import document_to_markdown


def test_optional_sections_availability_context_and_career_break_e2e(tmp_path: Path) -> None:
    md = """---
schema: cv-md/1.1
name: Lotte van Dijk
headline: Senior Cloud Engineer
location: Amsterdam, Netherlands
work_authorization: EU Citizen
availability: 1 month notice
email: lotte@example.nl
phone: "+31 6 1234 5678"
links:
  - label: GitHub
    url: https://github.com/lottevd
paper: a4
lang: en
---

## Summary

Cloud engineer specializing in Kubernetes reliability and automated infrastructure across European fintech platforms.

## Experience

### Senior Cloud Engineer — PayFlow NL
*2024-02 – Present | Amsterdam, Netherlands (Hybrid)*

Series B European payments scale-up, 85 employees.

- Cut Kubernetes cluster costs by 32% using Terraform autoscaling and spot node pools.

### Career Break — Relocation & Independent Study
*2023-06 – 2024-01 | Amsterdam, Netherlands*

- Completed Dutch B1 coursework and earned CNCF Kubernetes certification.

## Skills

- **Infrastructure:** Kubernetes, Terraform

## Education

### M.Sc. Computer Science — TU Delft
*2017 – 2019 | Delft, Netherlands*

## Languages

- **Dutch:** Native
- **English:** C2 (Proficient / Working Language)

## Certifications

- **CKA: Certified Kubernetes Administrator** — CNCF (2024-01 – 2027-01, ID: `LF-98231`) | [Verify](https://training.linuxfoundation.org/verify)

## Awards

- **Dutch DevOps Award** — DevOpsDays Amsterdam (2024) — Best platform reliability turnaround

## Speaking

- **Zero-Downtime Cluster Upgrades** — KubeCon Europe (2025-04) | [Slides](https://example.nl/slides)

## Volunteering

### Mentor — TechGrounds Amsterdam
*2023-03 – Present | Amsterdam, Netherlands*

- Mentored 10 junior cloud engineers on Terraform and Linux fundamentals.

## Courses

- **Distributed Systems Engineering** — MIT OpenCourseWare (2023)

## Interests

- **Interests:** Trail running, open-source typography

## Facts

- **Preference: Compensation** — Target €95K base.
"""
    doc = parse_cv_text(md)
    val = validate_cv(doc)
    assert val.ok, val.errors
    assert not val.warnings, val.warnings
    assert doc.frontmatter.availability == "1 month notice"

    # Writer round-trip preserves availability and all optional sections
    roundtrip = parse_cv_text(document_to_markdown(doc))
    assert roundtrip.frontmatter.availability == "1 month notice"
    assert [s.title for s in roundtrip.sections] == [s.title for s in doc.sections]

    # Render and verify PDF
    pdf_path = tmp_path / "lotte.pdf"
    compile_pdf(doc, pdf_path)
    report = verify_pdf(doc, pdf_path)
    assert report.ok, report.errors
    assert "1 month notice" in report.extracted_text
    assert "LF-98231" in report.extracted_text
    assert "Dutch DevOps Award" in report.extracted_text
    assert "TechGrounds Amsterdam" in report.extracted_text
    assert "Trail running" in report.extracted_text
    assert "€95K" not in report.extracted_text


def test_localized_eu_headings_nl_de_fr_validate_render_and_tailor(tmp_path: Path) -> None:
    dutch_md = """---
schema: cv-md/1.1
name: Bram de Vries
headline: Senior Backend Developer
location: Utrecht, Netherlands
availability: Direct beschikbaar
email: bram@example.nl
paper: a4
lang: nl
---

## Profiel

Backend-ontwikkelaar met 7 jaar ervaring in Python en PostgreSQL voor schaalbare betalingsplatformen.

## Werkervaring

### Senior Backend Developer — BetaalNL
*2022-01 – Present | Utrecht, Netherlands*

- Gebouwd aan Python API's en PostgreSQL-datamodellen voor 2M transacties per maand.

## Vaardigheden

- **Backend:** Python, PostgreSQL

## Opleiding

### B.Sc. Informatica — Universiteit Utrecht
*2015 – 2018 | Utrecht, Netherlands*

## Talen

- **Nederlands:** Moedertaal
- **Engels:** C2

## Certificeringen

- **AWS Certified Developer** — AWS (2024-03)

## Prijzen

- **Hackathon Winnaar** — FinTech NL (2023)

## Hobby’s

- **Interesses:** Wielrennen, koffie branden

## Feiten

- **Notitie: Salaris** — Geheime notitie die nooit op de PDF mag komen.
"""
    doc = parse_cv_text(dutch_md)
    val = validate_cv(doc)
    assert val.ok, val.errors
    assert not val.warnings, val.warnings
    assert doc.facts_section is not None
    assert doc.facts_section.title == "Feiten"
    assert all(s.title != "Feiten" for s in doc.renderable_sections)

    pdf_path = tmp_path / "bram-nl.pdf"
    compile_pdf(doc, pdf_path)
    report = verify_pdf(doc, pdf_path)
    assert report.ok, report.errors
    assert "Geheime notitie" not in report.extracted_text

    # Tailoring works cleanly on localized headings
    tailored, _ = tailor_strict(doc, "Python PostgreSQL backend", tailor_target="Backend NL", pages=2)
    assert validate_cv(tailored).ok

    # German & French headings validate with 0 warnings too
    german_md = """---
schema: cv-md/1.1
name: Anna Weber
email: anna@example.de
lang: de
---

## Profil

Erfahrene Produktmanagerin für B2B-SaaS-Plattformen.

## Berufserfahrung

### Product Manager — CloudWerk
*2021-01 – Present | Berlin, Germany*

- Leitete Roadmap für Analytics-Plattform mit SQL und Figma.

## Kenntnisse

- **Tools:** SQL, Figma

## Ausbildung

### M.Sc. Wirtschaftsinformatik — TU Berlin
*2016 – 2018*

## Sprachen

- **Deutsch:** Muttersprache
- **Englisch:** C1

## Zertifizierungen

- **PSPO I** — Scrum.org (2023)

## Fakten

- **Notiz:** Nur für interne Zwecke.
"""
    g_val = validate_cv(parse_cv_text(german_md))
    assert g_val.ok, g_val.errors
    assert not g_val.warnings, g_val.warnings

    french_md = """---
schema: cv-md/1.1
name: Camille Laurent
email: camille@example.fr
lang: fr
---

## Résumé

Ingénieure données spécialisée en Python et dbt.

## Expérience professionnelle

### Data Engineer — FinParis
*2022-04 – Present | Paris, France*

- Conçu des pipelines Python et dbt pour le reporting réglementaire.

## Compétences

- **Data:** Python, dbt

## Formation

### Master Data Science — Université Paris-Saclay
*2019 – 2021*

## Langues

- **Français:** Langue maternelle
- **Anglais:** C1

## Centres d’intérêt

- **Intérêts:** Cyclisme, typographie

## Faits

- **Note:** Confidentiel.
"""
    f_val = validate_cv(parse_cv_text(french_md))
    assert f_val.ok, f_val.errors
    assert not f_val.warnings, f_val.warnings


def test_importers_populate_rich_certifications_and_optional_sections(tmp_path: Path) -> None:
    # 1. LinkedIn ZIP with extended Certifications, Honors, Courses, Volunteering
    zip_path = tmp_path / "li-rich.zip"
    files = {
        "Profile.csv": 'First Name,Last Name,Headline,Summary,Geo Location,Websites\nEva,Jansen,Cloud Architect,"Building resilient cloud systems.","Amsterdam, Netherlands",\n',
        "Email Addresses.csv": "Email Address,Confirmed,Primary\neva@example.nl,Yes,Yes\n",
        "Positions.csv": 'Company Name,Title,Description,Location,Started On,Finished On\nAcme,Cloud Architect,"- Managed AWS and Kubernetes platforms.","Amsterdam, Netherlands",Jan 2022,\n',
        "Skills.csv": "Name\nAWS\nKubernetes\n",
        "Languages.csv": "Name,Proficiency\nEnglish,Full professional proficiency\n",
        "Certifications.csv": "Name,Authority,Started On,Finished On,License Number,Url\nCKA,CNCF,Jan 2024,Jan 2027,LF-123,https://example.org/verify\n",
        "Honors.csv": "Title,Issuer,Issued On,Description\nCloud Leader of the Year,CloudNL,Nov 2024,Recognized for open-source contributions\n",
        "Courses.csv": "Name,Number\nDistributed Systems,CS-401\n",
        "Volunteering.csv": 'Company Name,Role,Started On,Finished On,Description\nCodeNL,Mentor,Mar 2023,,"- Coached 8 students."\n',
    }
    with zipfile.ZipFile(zip_path, "w") as zf:
        for k, v in files.items():
            zf.writestr(k, v)

    md_li = import_linkedin(zip_path)
    assert "ID: `LF-123`" in md_li
    assert "[Verify](https://example.org/verify)" in md_li
    assert "## Awards" in md_li
    assert "## Volunteering" in md_li
    assert "## Courses" in md_li
    assert validate_cv(parse_cv_text(md_li)).ok

    # 2. JSON Resume with certificates URL, awards, volunteer, interests
    jr = {
        "basics": {"name": "Eva Jansen", "email": "eva@example.nl"},
        "work": [{"name": "Acme", "position": "Engineer", "startDate": "2022-01", "highlights": ["Built Python services."]}],
        "languages": [{"language": "English", "fluency": "C2"}],
        "certificates": [{"name": "CKA", "issuer": "CNCF", "date": "2024-05", "url": "https://example.org/cka"}],
        "awards": [{"title": "Best OSS Tool", "awarder": "PyCon", "date": "2024", "summary": "Community award"}],
        "volunteer": [{"organization": "PyLadies", "position": "Organizer", "startDate": "2023-01", "highlights": ["Hosted 6 workshops."]}],
        "interests": [{"name": "Cycling"}, {"name": "Typography"}],
    }
    md_jr = convert_json_resume(jr)
    assert "[Verify](https://example.org/cka)" in md_jr
    assert "## Awards" in md_jr
    assert "## Volunteering" in md_jr
    assert "## Interests" in md_jr
    assert "Cycling, Typography" in md_jr
    assert validate_cv(parse_cv_text(md_jr)).ok
    # Canonical section ordering: Languages precedes Certifications
    assert md_jr.index("## Languages") < md_jr.index("## Certifications")


def test_review_regressions_multiline_honors_html_and_localized_facts() -> None:
    from cvfmt.linkedin import _build_cv_markdown
    from cvfmt.url_import import convert_html_cv

    # 1. Multiline honor summary collapses to single line; blank items don't emit empty headings; bad URL/backtick ID sanitized
    md = _build_cv_markdown(
        name="Alex Dev",
        email="alex@example.com",
        positions=[{"company": "Acme", "title": "Engineer", "start": "2023-01", "end": "Present", "location": "", "bullets": ["Built APIs."]}],
        languages=[("English", "C2")],
        certifications=[
            {"name": "", "authority": "Empty", "date": "2024"},
            {"name": "CKA", "authority": "CNCF", "date": "2024-01", "credential_id": "ID`123`", "url": "https://bad url/verify"},
        ],
        awards=[{"title": "Best Award", "awarder": "Org", "date": "2024", "summary": "Line one\nLine two"}],
        courses=[{"name": "", "provider": "Empty", "date": ""}],
    )
    assert "## Courses" not in md
    assert "ID: `ID123`" in md
    assert "[Verify]" not in md
    assert "Line one Line two" in md
    assert md.index("## Languages") < md.index("## Certifications") < md.index("## Awards")
    assert validate_cv(parse_cv_text(md)).ok

    # 2. Short <p> words inside Experience do not hijack HTML section parsing; real <h2> optional sections are preserved
    html = """
    <html><head><title>CV – Jane</title></head><body><main>
      <h2>Experience</h2>
      <h3>Engineer @ Acme</h3>
      <p>2023-01 – Present</p>
      <p>Engagement</p>
      <p>Shipped high-throughput Go services.</p>
      <h2>Certifications</h2>
      <p>CKA — CNCF (2024)</p>
      <a href="mailto:jane@example.com">Email</a>
    </main></body></html>
    """
    md_html = convert_html_cv(html)
    assert "Shipped high-throughput Go services." in md_html
    assert "## Certifications" in md_html
    assert "CKA" in md_html

    # 3. Tailoring a Dutch CV without ## Feiten creates ## Feiten (not English ## Facts) when pruning/stripping
    nl_md = """---
schema: cv-md/1.1
name: Bram
email: bram@example.nl
lang: nl
tailor_mode: dreamer
---

## Werkervaring

### Engineer — Acme
*2023-01 – Present | Utrecht, Netherlands*

- Gebouwd aan Python API's.
- **(Aspirational)** Schaalde naar 10M gebruikers.

## Talen

- **Nederlands:** Moedertaal
"""
    tailored, _ = tailor_strict(parse_cv_text(nl_md), "Python API", tailor_target="Backend NL", pages=2)
    assert tailored.facts_section is not None
    assert tailored.facts_section.title == "Feiten"
    assert validate_cv(tailored).ok

