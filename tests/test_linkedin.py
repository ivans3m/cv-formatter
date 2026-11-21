"""Tests for LinkedIn export (.zip / CSV folder / Save-to-PDF) -> cv-md/1.0 -> PDF."""

from __future__ import annotations

import zipfile
from pathlib import Path

from typer.testing import CliRunner

from cvfmt.cli import app
from cvfmt.linkedin import import_linkedin, map_linkedin_proficiency, normalize_linkedin_date
from cvfmt.parser import parse_cv_text
from cvfmt.validator import validate_cv


def _create_sample_linkedin_zip(zip_path: Path) -> None:
    files = {
        "Profile.csv": (
            "First Name,Last Name,Headline,Summary,Geo Location,Websites\n"
            "Anna,Kowalska,Senior Product Designer,Designing B2B SaaS workflows across Europe.,Amsterdam, Netherlands,[PERSONAL:https://annakowalska.eu]\n"
        ),
        "Email Addresses.csv": (
            "Email Address,Confirmed,Primary\n"
            "anna@kowalska.eu,Yes,Yes\n"
        ),
        "Positions.csv": (
            "Company Name,Title,Description,Location,Started On,Finished On\n"
            "NordicPay,Lead Product Designer,\"- Led checkout redesign lifting conversion by 18%.\n- Built shared Figma design system for 5 squads.\",Amsterdam, Netherlands,Jan 2024,\n"
            "NordicPay,Senior Product Designer,- Owned merchant onboarding flows for 12K SMBs.,Amsterdam, Netherlands,Mar 2022,Dec 2023\n"
            "Studio Delta,Product Designer,- Shipped 10+ web apps for European fintech clients.,Warsaw, Poland,Jun 2019,Feb 2022\n"
        ),
        "Education.csv": (
            "School Name,Start Date,End Date,Notes,Degree Name,Activities\n"
            "University of Warsaw,2015,2019,,B.A. Cognitive Science,\n"
        ),
        "Skills.csv": "Name\nFigma\nDesign Systems\nUser Research\nPrototyping\n",
        "Languages.csv": (
            "Name,Proficiency\n"
            "Polish,Native or bilingual proficiency\n"
            "English,Full professional proficiency\n"
            "Dutch,Limited working proficiency\n"
        ),
        "Certifications.csv": (
            "Name,Authority,Started On\n"
            "NN/g UX Certification,Nielsen Norman Group,May 2023\n"
        ),
    }
    # Fix Geo Location comma quoting properly
    files["Profile.csv"] = (
        'First Name,Last Name,Headline,Summary,Geo Location,Websites\n'
        'Anna,Kowalska,Senior Product Designer,"Designing B2B SaaS workflows across Europe.","Amsterdam, Netherlands",[PERSONAL:https://annakowalska.eu]\n'
    )
    files["Positions.csv"] = (
        'Company Name,Title,Description,Location,Started On,Finished On\n'
        'NordicPay,Lead Product Designer,"- Led checkout redesign lifting conversion by 18%.\n- Built shared Figma design system for 5 squads.","Amsterdam, Netherlands",Jan 2024,\n'
        'NordicPay,Senior Product Designer,"- Owned merchant onboarding flows for 12K SMBs.","Amsterdam, Netherlands",Mar 2022,Dec 2023\n'
        'Studio Delta,Product Designer,"- Shipped 10+ web apps for European fintech clients.","Warsaw, Poland",Jun 2019,Feb 2022\n'
    )
    with zipfile.ZipFile(zip_path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)


def test_linkedin_date_and_cefr_helpers() -> None:
    assert normalize_linkedin_date("Apr 2023") == "2023-04"
    assert normalize_linkedin_date("January 2021") == "2021-01"
    assert normalize_linkedin_date("Present") == "Present"
    assert normalize_linkedin_date("2019") == "2019"

    assert map_linkedin_proficiency("Native or bilingual proficiency") == "Native"
    assert "C2" in map_linkedin_proficiency("Full professional proficiency")
    assert "C1" in map_linkedin_proficiency("Professional working proficiency")
    assert "B1" in map_linkedin_proficiency("Limited working proficiency")


def test_linkedin_zip_import_groups_promotions_and_validates(tmp_path: Path) -> None:
    zip_path = tmp_path / "linkedin-export.zip"
    _create_sample_linkedin_zip(zip_path)

    md_text = import_linkedin(zip_path)
    doc = parse_cv_text(md_text)
    val = validate_cv(doc)
    assert val.ok, val.errors
    assert doc.frontmatter.name == "Anna Kowalska"
    assert doc.frontmatter.email == "anna@kowalska.eu"
    assert doc.frontmatter.location == "Amsterdam, Netherlands"

    exp = next(s for s in doc.sections if s.title == "Experience")
    # NordicPay's two consecutive roles should be grouped into 1 entry with 2 sub_roles
    assert len(exp.entries) == 2
    assert exp.entries[0].primary == "NordicPay"
    assert len(exp.entries[0].sub_roles) == 2
    assert exp.entries[0].sub_roles[0].title == "Lead Product Designer"
    assert exp.entries[0].sub_roles[1].title == "Senior Product Designer"


def test_cli_linkedin_zip_to_pdf_verified(tmp_path: Path) -> None:
    zip_path = tmp_path / "linkedin-export.zip"
    _create_sample_linkedin_zip(zip_path)
    pdf_out = tmp_path / "anna-cv.pdf"

    runner = CliRunner()
    res = runner.invoke(
        app,
        ["linkedin", str(zip_path), "--pdf", "-o", str(pdf_out), "--verify"],
    )
    assert res.exit_code == 0, res.output
    assert pdf_out.exists()
    assert pdf_out.with_suffix(".md").exists()


def test_linkedin_two_column_pdf_import_and_render(tmp_path: Path) -> None:
    """Simulate a LinkedIn 2-column 'Save to PDF' export and convert it to cv-md/1.0 + PDF."""
    import typst
    from cvfmt.renderer import FONTS_DIR

    fake_li_typ = r"""
#set page(paper: "us-letter", margin: 12mm)
#set text(font: "IBM Plex Sans", size: 9pt)
#grid(
  columns: (30%, 66%),
  gutter: 4%,
  [
    Contact
    \
    marco.rossi\@example.it
    \
    +39 340 123 4567
    \
    www.linkedin.com/in/marcorossi
    \
    Top Skills
    \
    Python
    \
    Kubernetes
    \
    Languages
    \
    Italian (Native or bilingual)
    \
    English (Full professional)
  ],
  [
    Marco Rossi
    \
    Senior Platform Engineer
    \
    Milan, Italy
    \
    Summary
    \
    Platform engineer focused on reliable cloud systems across Europe.
    \
    Experience
    \
    CloudItalia
    \
    Senior Platform Engineer
    \
    March 2022 - Present (4 years)
    \
    Milan, Italy
    \
    Built Kubernetes clusters serving 2M daily users.
    \
    Education
    \
    Politecnico di Milano
    \
    M.Sc. Computer Engineering · (2016 - 2018)
  ],
)
"""
    li_pdf = tmp_path / "Profile.pdf"
    orig_bytes = typst.compile(
        fake_li_typ.encode("utf-8"), font_paths=[str(FONTS_DIR)], ignore_system_fonts=True
    )
    li_pdf.write_bytes(orig_bytes)

    # Without -o, cvfmt linkedin Profile.pdf --pdf must write Profile-cv.pdf and NOT overwrite Profile.pdf
    runner = CliRunner()
    res = runner.invoke(app, ["linkedin", str(li_pdf), "--pdf", "--verify"])
    assert res.exit_code == 0, res.output
    out_pdf = tmp_path / "Profile-cv.pdf"
    assert out_pdf.exists()
    assert li_pdf.read_bytes() == orig_bytes
    md_text = out_pdf.with_suffix(".md").read_text(encoding="utf-8")
    assert "Marco Rossi" in md_text
    assert "marco.rossi@example.it" in md_text
    assert "CloudItalia" in md_text
    assert "C2" in md_text
