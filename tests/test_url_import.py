"""Tests for cvfmt from-url (HTML CV pages, JSON Resume, raw cv-md/1.0, LinkedIn authwall notice)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from cvfmt.cli import app
from cvfmt.parser import parse_cv_text
from cvfmt.url_import import (
    LinkedInAuthwallError,
    convert_html_cv,
    convert_json_resume,
    import_from_url,
    is_linkedin_url,
)
from cvfmt.validator import validate_cv


def test_linkedin_url_rejected_with_helpful_guidance() -> None:
    assert is_linkedin_url("https://www.linkedin.com/in/ivans3m/")
    with pytest.raises(LinkedInAuthwallError, match="Save to PDF"):
        import_from_url("https://www.linkedin.com/in/ivans3m/")


def test_json_resume_conversion_validates() -> None:
    sample = {
        "basics": {
            "name": "Clara Lindholm",
            "label": "Senior Data Engineer",
            "email": "clara@lindholm.se",
            "phone": "+46 70 111 2233",
            "url": "https://lindholm.se",
            "summary": "Data engineer building streaming analytics in Python and SQL.",
            "location": {"city": "Stockholm", "countryCode": "Sweden"},
            "profiles": [{"network": "GitHub", "url": "https://github.com/claralindholm"}],
        },
        "work": [
            {
                "name": "NordData AB",
                "position": "Senior Data Engineer",
                "startDate": "2022-03",
                "highlights": ["Cut BigQuery warehouse costs by 35% (€18K/month)."],
            }
        ],
        "education": [
            {
                "institution": "KTH",
                "studyType": "M.Sc.",
                "area": "Data Science",
                "startDate": "2017",
                "endDate": "2019",
            }
        ],
        "skills": [{"name": "Data", "keywords": ["Python", "SQL", "BigQuery"]}],
        "languages": [{"language": "Swedish", "fluency": "Native"}, {"language": "English", "fluency": "C2"}],
    }
    md = convert_json_resume(sample)
    doc = parse_cv_text(md)
    res = validate_cv(doc)
    assert res.ok, res.errors
    assert doc.frontmatter.name == "Clara Lindholm"
    assert doc.frontmatter.location == "Stockholm, Sweden"


def test_html_cv_page_conversion() -> None:
    sample_html = """
    <html>
      <head><title>CV – courtesy of Ivan Diuldia</title></head>
      <body>
        <main>
          <h1>CV</h1>
          <h2>Summary</h2>
          <p>Creative director and digital strategist with 20 years of experience.</p>
          <h2>Employment</h2>
          <h3>Digital Marketing Consultant @ IT-Compass</h3>
          <p>2024 – 2026</p>
          <p>Haarlem, the Netherlands</p>
          <p>Advise Netherlands-based startups on AI integration and growth strategy.</p>
          <h2>Education</h2>
          <p>National Technical University "Kharkiv Polytechnic Institute"</p>
          <p>2000–2005 – System Analyst Engineer</p>
          <h2>Skills</h2>
          <p>Digital Strategy, Python, Figma</p>
          <a href="mailto:ivan@diuldia.com">Email</a>
          <a href="https://www.linkedin.com/in/ivans3m/">LinkedIn</a>
        </main>
      </body>
    </html>
    """
    md = convert_html_cv(sample_html, source_url="https://ivan.diuldia.com/cv/")
    doc = parse_cv_text(md)
    res = validate_cv(doc)
    assert res.ok, res.errors
    assert doc.frontmatter.name == "Ivan Diuldia"
    assert doc.frontmatter.email == "ivan@diuldia.com"
    exp = next(s for s in doc.sections if s.title == "Experience")
    assert exp.entries[0].primary == "Digital Marketing Consultant"
    assert exp.entries[0].secondary == "IT-Compass"


def test_cli_from_url_json_resume_to_pdf_verified(tmp_path: Path) -> None:
    payload = json.dumps(
        {
            "basics": {
                "name": "Clara Lindholm",
                "label": "Senior Data Engineer",
                "email": "clara@lindholm.se",
                "location": {"city": "Stockholm", "countryCode": "Sweden"},
            },
            "work": [
                {
                    "name": "NordData AB",
                    "position": "Senior Data Engineer",
                    "startDate": "2022-03",
                    "highlights": ["Cut BigQuery costs by 35%."],
                }
            ],
            "languages": [{"language": "English", "fluency": "C2"}],
        }
    )
    pdf_out = tmp_path / "clara.pdf"
    runner = CliRunner()
    with patch("cvfmt.url_import.fetch_url", return_value=(payload, "application/json")):
        res = runner.invoke(
            app,
            ["from-url", "https://example.se/resume.json", "--pdf", "-o", str(pdf_out), "--verify"],
        )
    assert res.exit_code == 0, res.output
    assert pdf_out.exists()
    assert pdf_out.with_suffix(".md").exists()
