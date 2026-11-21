"""Import LinkedIn exports (Data Export ZIP/CSV folder or 'Save to PDF') into cv-md/1.0."""

from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import datetime
from pathlib import Path

import pdfplumber


_MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}

_PROFICIENCY_TO_CEFR = {
    "native or bilingual": "Native",
    "full professional": "C2 (Proficient / Working Language)",
    "professional working": "C1 (Advanced)",
    "limited working": "B1 (Intermediate)",
    "elementary": "A2 (Basic)",
}

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
_LINKEDIN_URL_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+", re.I)
_DATE_LINE_RE = re.compile(
    r"^([A-Za-z]+\s+\d{4}|\d{4})\s*[-–—]\s*(Present|[A-Za-z]+\s+\d{4}|\d{4})(?:\s*\([^)]*\))?$",
    re.I,
)


def normalize_linkedin_date(raw: str | None) -> str:
    """Convert LinkedIn date strings ('Apr 2023', 'January 2021', '2020', 'Present') to cv-md/1.0."""
    if not raw:
        return ""
    s = raw.strip()
    if not s:
        return ""
    if s.lower() == "present":
        return "Present"
    if re.match(r"^\d{4}-\d{2}$", s) or re.match(r"^\d{4}$", s):
        return s
    parts = s.split()
    if len(parts) == 2 and parts[0].lower() in _MONTH_MAP and re.match(r"^\d{4}$", parts[1]):
        return f"{parts[1]}-{_MONTH_MAP[parts[0].lower()]}"
    for fmt in ("%b %Y", "%B %Y", "%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m")
        except ValueError:
            pass
    m_year = re.search(r"\b(\d{4})\b", s)
    return m_year.group(1) if m_year else s


def map_linkedin_proficiency(raw: str | None) -> str:
    """Map LinkedIn language proficiency labels to EU CEFR levels."""
    if not raw:
        return "B2 (Upper Intermediate)"
    low = raw.strip().lower()
    for key, cefr in _PROFICIENCY_TO_CEFR.items():
        if key in low:
            return cefr
    if re.search(r"\b(a1|a2|b1|b2|c1|c2|native)\b", low):
        return raw.strip()
    return raw.strip()


def _yaml_quote(val: str) -> str:
    escaped = val.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _description_to_bullets(desc: str) -> list[str]:
    if not desc or not desc.strip():
        return []
    bullets: list[str] = []
    for raw_line in desc.splitlines():
        cleaned = re.sub(r"^\s*[•\-–—*]\s*", "", raw_line).strip()
        if cleaned:
            bullets.append(cleaned)
    return bullets


def _build_cv_markdown(
    *,
    name: str,
    headline: str = "",
    location: str = "",
    email: str = "",
    phone: str = "",
    links: list[tuple[str, str]] | None = None,
    summary: str = "",
    positions: list[dict] | None = None,
    education: list[dict] | None = None,
    skills: list[str] | None = None,
    languages: list[tuple[str, str]] | None = None,
    certifications: list[dict] | None = None,
    paper: str = "a4",
) -> str:
    """Assemble a clean, valid cv-md/1.0 Markdown string from normalized LinkedIn fields."""
    lines: list[str] = [
        "---",
        "schema: cv-md/1.0",
        f"name: {_yaml_quote(name or '[TODO: add full name]')}",
    ]
    if headline:
        lines.append(f"headline: {_yaml_quote(headline)}")
    if location:
        lines.append(f"location: {_yaml_quote(location)}")
    lines.append(f"email: {_yaml_quote(email or '[TODO: add email]')}")
    if phone:
        lines.append(f"phone: {_yaml_quote(phone)}")
    if links:
        lines.append("links:")
        for label, url in links:
            lines.append(f"  - label: {_yaml_quote(label)}")
            lines.append(f"    url: {url}")
    lines.extend([f"paper: {paper}", "lang: en", "---", ""])

    if summary:
        lines.extend(["## Summary", "", re.sub(r"\s+", " ", summary).strip(), ""])

    lines.extend(["## Experience", ""])
    pos_list = positions or []
    if not pos_list:
        lines.extend(["### [TODO: Role Title] — [TODO: Company]", "*2024-01 – Present*", "", "- [TODO: Add achievements]", ""])
    else:
        # Group consecutive roles at the same company into #### sub-roles
        idx = 0
        while idx < len(pos_list):
            comp = pos_list[idx].get("company", "").strip()
            group = [pos_list[idx]]
            while idx + 1 < len(pos_list) and comp and pos_list[idx + 1].get("company", "").strip().lower() == comp.lower():
                idx += 1
                group.append(pos_list[idx])
            idx += 1

            if len(group) == 1:
                p = group[0]
                title = p.get("title", "").strip() or "Role"
                company = p.get("company", "").strip()
                heading = f"### {title} — {company}" if company else f"### {title}"
                start = normalize_linkedin_date(p.get("start"))
                end = normalize_linkedin_date(p.get("end")) or "Present"
                date_part = f"{start} – {end}" if start else end
                loc = p.get("location", "").strip()
                meta = f"{date_part} | {loc}" if loc else date_part
                lines.extend([heading, f"*{meta}*", ""])
                for b in p.get("bullets", []):
                    lines.append(f"- {b}")
                if p.get("bullets"):
                    lines.append("")
            else:
                earliest_start = normalize_linkedin_date(group[-1].get("start"))
                latest_end = normalize_linkedin_date(group[0].get("end")) or "Present"
                overall_date = f"{earliest_start} – {latest_end}" if earliest_start else latest_end
                loc = next((g.get("location", "").strip() for g in group if g.get("location")), "")
                meta = f"{overall_date} | {loc}" if loc else overall_date
                lines.extend([f"### {comp}", f"*{meta}*", ""])
                for g in group:
                    g_title = g.get("title", "").strip() or "Role"
                    g_start = normalize_linkedin_date(g.get("start"))
                    g_end = normalize_linkedin_date(g.get("end")) or "Present"
                    g_date = f"{g_start} – {g_end}" if g_start else g_end
                    lines.append(f"#### {g_title} *({g_date})*")
                    for b in g.get("bullets", []):
                        lines.append(f"- {b}")
                    lines.append("")

    if skills:
        deduped = list(dict.fromkeys(s.strip() for s in skills if s.strip()))
        lines.extend(["## Skills", "", f"- **Core Skills:** {', '.join(deduped)}", ""])

    if education:
        lines.extend(["## Education", ""])
        for ed in education:
            degree = ed.get("degree", "").strip() or "Degree"
            school = ed.get("school", "").strip()
            heading = f"### {degree} — {school}" if school else f"### {degree}"
            start = normalize_linkedin_date(ed.get("start"))
            end = normalize_linkedin_date(ed.get("end"))
            date_part = f"{start} – {end}" if (start and end) else (start or end)
            lines.append(heading)
            if date_part:
                lines.append(f"*{date_part}*")
            lines.append("")
            for note in ed.get("bullets", []):
                lines.append(f"- {note}")
            if ed.get("bullets"):
                lines.append("")

    if certifications:
        lines.extend(["## Certifications", ""])
        for c in certifications:
            c_name = c.get("name", "").strip()
            auth = c.get("authority", "").strip()
            year = normalize_linkedin_date(c.get("date"))[:4]
            if not c_name:
                continue
            suffix = f" — {auth}" if auth else ""
            if year:
                suffix += f" ({year})"
            lines.append(f"- **{c_name}**{suffix}")
        lines.append("")

    if languages:
        lines.extend(["## Languages", ""])
        for lang_name, level in languages:
            if lang_name.strip():
                lines.append(f"- **{lang_name.strip()}:** {map_linkedin_proficiency(level)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _read_csv_rows(source: Path | zipfile.ZipFile, filename: str) -> list[dict[str, str]]:
    if isinstance(source, zipfile.ZipFile):
        match = next((n for n in source.namelist() if Path(n).name.lower() == filename.lower()), None)
        if not match:
            return []
        raw = source.read(match).decode("utf-8-sig", errors="replace")
        return list(csv.DictReader(io.StringIO(raw)))
    p = source / filename
    if not p.exists():
        # Case-insensitive fallback
        found = next((f for f in source.iterdir() if f.name.lower() == filename.lower()), None)
        if not found:
            return []
        p = found
    with p.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def import_linkedin_archive(source_path: Path, *, paper: str = "a4") -> str:
    """Import a LinkedIn official Data Export (.zip or extracted directory of CSVs)."""
    if source_path.is_file() and source_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(source_path, "r") as zf:
            return _parse_csv_bundle(zf, paper=paper)
    if source_path.is_dir():
        return _parse_csv_bundle(source_path, paper=paper)
    raise ValueError(f"Expected a LinkedIn .zip archive or CSV directory, got {source_path}")


def _parse_csv_bundle(source: Path | zipfile.ZipFile, *, paper: str) -> str:
    profile_rows = _read_csv_rows(source, "Profile.csv")
    email_rows = _read_csv_rows(source, "Email Addresses.csv")
    pos_rows = _read_csv_rows(source, "Positions.csv")
    edu_rows = _read_csv_rows(source, "Education.csv")
    skill_rows = _read_csv_rows(source, "Skills.csv")
    lang_rows = _read_csv_rows(source, "Languages.csv")
    cert_rows = _read_csv_rows(source, "Certifications.csv")

    prof = profile_rows[0] if profile_rows else {}
    first = prof.get("First Name", "").strip()
    last = prof.get("Last Name", "").strip()
    name = f"{first} {last}".strip()
    headline = prof.get("Headline", "").strip()
    summary = prof.get("Summary", "").strip()
    location = prof.get("Geo Location", "").strip()

    email = ""
    for er in email_rows:
        addr = er.get("Email Address", "").strip()
        if addr and er.get("Primary", "").strip().lower() in ("yes", "true", "1"):
            email = addr
            break
    if not email and email_rows:
        email = email_rows[0].get("Email Address", "").strip()

    links: list[tuple[str, str]] = []
    websites_raw = prof.get("Websites", "").strip()
    for url in re.findall(r"https?://[^\s,\]]+", websites_raw):
        links.append(("Website", url.rstrip("),;")))

    positions: list[dict] = []
    for pr in pos_rows:
        positions.append(
            {
                "company": pr.get("Company Name", "").strip(),
                "title": pr.get("Title", "").strip(),
                "start": pr.get("Started On", "").strip(),
                "end": pr.get("Finished On", "").strip() or "Present",
                "location": pr.get("Location", "").strip(),
                "bullets": _description_to_bullets(pr.get("Description", "")),
            }
        )

    education: list[dict] = []
    for er in edu_rows:
        notes = _description_to_bullets(er.get("Notes", "") or er.get("Activities", ""))
        education.append(
            {
                "school": er.get("School Name", "").strip(),
                "degree": er.get("Degree Name", "").strip() or "Education",
                "start": er.get("Start Date", "").strip(),
                "end": er.get("End Date", "").strip(),
                "bullets": notes,
            }
        )

    skills = [sr.get("Name", "").strip() for sr in skill_rows if sr.get("Name", "").strip()]
    languages = [
        (lr.get("Name", "").strip(), lr.get("Proficiency", "").strip())
        for lr in lang_rows
        if lr.get("Name", "").strip()
    ]
    certifications = [
        {
            "name": cr.get("Name", "").strip(),
            "authority": cr.get("Authority", "").strip(),
            "date": cr.get("Started On", "").strip(),
        }
        for cr in cert_rows
        if cr.get("Name", "").strip()
    ]

    return _build_cv_markdown(
        name=name,
        headline=headline,
        location=location,
        email=email,
        links=links,
        summary=summary,
        positions=positions,
        education=education,
        skills=skills,
        languages=languages,
        certifications=certifications,
        paper=paper,
    )


def import_linkedin_pdf(pdf_path: Path, *, paper: str = "a4") -> str:
    """Import a LinkedIn 'Save to PDF' export using column-aware pdfplumber extraction."""
    left_lines: list[str] = []
    right_lines: list[str] = []

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            split_x = page.width * 0.34
            left_text = page.crop((0, 0, split_x, page.height)).extract_text() or ""
            right_text = page.crop((split_x, 0, page.width, page.height)).extract_text() or ""
            for ln in left_text.splitlines():
                s = ln.strip()
                if s and not re.match(r"^Page \d+ of \d+$", s, re.I):
                    left_lines.append(s)
            for ln in right_text.splitlines():
                s = ln.strip()
                if s and not re.match(r"^Page \d+ of \d+$", s, re.I):
                    right_lines.append(s)

    # Parse left sidebar (Contact, Top Skills, Languages, Certifications)
    sidebar_sections: dict[str, list[str]] = {}
    cur_side = "Contact"
    sidebar_headers = {"contact", "top skills", "languages", "certifications", "honors-awards"}
    for ln in left_lines:
        if ln.lower() in sidebar_headers:
            cur_side = ln.lower()
            sidebar_sections.setdefault(cur_side, [])
        else:
            sidebar_sections.setdefault(cur_side, []).append(ln)

    contact_blob = "\n".join(sidebar_sections.get("contact", []))
    email_m = _EMAIL_RE.search(contact_blob)
    email = email_m.group(0) if email_m else ""
    phone_m = _PHONE_RE.search(contact_blob)
    phone = phone_m.group(0).strip() if phone_m else ""
    links: list[tuple[str, str]] = []
    li_m = _LINKEDIN_URL_RE.search(contact_blob)
    if li_m:
        u = li_m.group(0)
        if not u.startswith("http"):
            u = f"https://{u}"
        links.append(("LinkedIn", u))

    skills = sidebar_sections.get("top skills", [])

    languages: list[tuple[str, str]] = []
    lang_raw = sidebar_sections.get("languages", [])
    i = 0
    while i < len(lang_raw):
        ln = lang_raw[i]
        m_inline = re.match(r"^([^(]+?)\s*\(([^)]+)\)$", ln)
        if m_inline:
            languages.append((m_inline.group(1).strip(), m_inline.group(2).strip()))
            i += 1
        elif i + 1 < len(lang_raw) and lang_raw[i + 1].startswith("("):
            languages.append((ln, lang_raw[i + 1].strip("()")))
            i += 2
        else:
            languages.append((ln, ""))
            i += 1

    certifications = [{"name": c, "authority": "", "date": ""} for c in sidebar_sections.get("certifications", [])]

    # Parse right main column (Name, Headline, Location, Summary, Experience, Education)
    main_headers = {"summary", "experience", "education"}
    header_lines: list[str] = []
    main_sections: dict[str, list[str]] = {}
    cur_main: str | None = None
    for ln in right_lines:
        if ln.lower() in main_headers:
            cur_main = ln.lower()
            main_sections.setdefault(cur_main, [])
        elif cur_main is None:
            header_lines.append(ln)
        else:
            main_sections[cur_main].append(ln)

    name = header_lines[0] if len(header_lines) >= 1 else ""
    headline = header_lines[1] if len(header_lines) >= 2 else ""
    location = header_lines[2] if len(header_lines) >= 3 else ""
    summary = " ".join(main_sections.get("summary", []))

    # Parse Experience entries by anchoring on LinkedIn date lines
    exp_lines = main_sections.get("experience", [])
    positions: list[dict] = []
    date_indices = [idx for idx, ln in enumerate(exp_lines) if _DATE_LINE_RE.match(ln)]
    for pos_i, d_idx in enumerate(date_indices):
        m_date = _DATE_LINE_RE.match(exp_lines[d_idx])
        assert m_date is not None
        start_raw, end_raw = m_date.group(1), m_date.group(2)
        title = exp_lines[d_idx - 1] if d_idx >= 1 else "Role"
        company = exp_lines[d_idx - 2] if d_idx >= 2 else ""
        # Determine where the description for this role ends (2 lines before next date line)
        next_start = date_indices[pos_i + 1] - 2 if pos_i + 1 < len(date_indices) else len(exp_lines)
        desc_lines = exp_lines[d_idx + 1 : max(d_idx + 1, next_start)]
        loc = ""
        if desc_lines and len(desc_lines[0]) < 60 and "," in desc_lines[0] and not desc_lines[0].endswith("."):
            loc = desc_lines[0]
            desc_lines = desc_lines[1:]
        bullets = _description_to_bullets("\n".join(desc_lines))
        positions.append(
            {
                "company": company,
                "title": title,
                "start": start_raw,
                "end": end_raw,
                "location": loc,
                "bullets": bullets,
            }
        )

    # Parse Education lines
    edu_lines = main_sections.get("education", [])
    education: list[dict] = []
    for idx in range(0, len(edu_lines), 2):
        school = edu_lines[idx]
        detail = edu_lines[idx + 1] if idx + 1 < len(edu_lines) else ""
        m_dates = re.search(r"·\s*\(([^)]+)\)", detail)
        date_str = m_dates.group(1) if m_dates else ""
        degree = re.sub(r"·\s*\([^)]+\)", "", detail).strip(" ·,") or "Education"
        start_e, end_e = "", ""
        if "-" in date_str or "–" in date_str:
            parts = re.split(r"\s*[-–]\s*", date_str, maxsplit=1)
            start_e, end_e = parts[0].strip(), parts[1].strip()
        education.append({"school": school, "degree": degree, "start": start_e, "end": end_e, "bullets": []})

    return _build_cv_markdown(
        name=name,
        headline=headline,
        location=location,
        email=email,
        phone=phone,
        links=links,
        summary=summary,
        positions=positions,
        education=education,
        skills=skills,
        languages=languages,
        certifications=certifications,
        paper=paper,
    )


def import_linkedin(source_path: str | Path, *, paper: str = "a4") -> str:
    """Auto-detect LinkedIn export format (.pdf, .zip, or CSV directory) and return cv-md/1.0 text."""
    p = Path(source_path)
    if p.is_file() and p.suffix.lower() == ".pdf":
        return import_linkedin_pdf(p, paper=paper)
    if p.is_dir() or (p.is_file() and p.suffix.lower() == ".zip"):
        return import_linkedin_archive(p, paper=paper)
    raise ValueError(
        f"Unsupported LinkedIn input {p}. Pass a LinkedIn 'Save to PDF' (.pdf), Data Export (.zip), or CSV directory."
    )
