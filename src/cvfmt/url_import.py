"""Import public CV webpages (HTML), JSON Resume URLs, or raw cv-md/1.0 URLs."""

from __future__ import annotations

import json
import re
import urllib.request
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse

from cvfmt.linkedin import _build_cv_markdown
from cvfmt.models import LOCALIZED_SECTION_ALIASES, NON_RENDERED_SECTIONS, SUPPORTED_SCHEMAS


MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB safety limit


class LinkedInAuthwallError(ValueError):
    """Raised when a direct LinkedIn profile URL is passed."""


_CORE_HTML_SECTIONS = frozenset({"summary", "experience", "education", "skills"})
_OPTIONAL_HTML_SECTIONS = frozenset({"languages", "certifications", "awards", "courses", "interests"})
_SUPPORTED_HTML_SECTIONS = _CORE_HTML_SECTIONS | _OPTIONAL_HTML_SECTIONS

_SECTION_ALIASES: dict[str, str] = {
    **{
        k: v
        for k, v in LOCALIZED_SECTION_ALIASES.items()
        if v not in NON_RENDERED_SECTIONS and v in _SUPPORTED_HTML_SECTIONS
    },
    "about": "summary",
    "profile": "summary",
    "bio": "summary",
    "employment": "experience",
    "work": "experience",
    "work experience": "experience",
    "career": "experience",
    "technologies": "skills",
    "tech stack": "skills",
    "certificates": "certifications",
    "honors": "awards",
    "honors & awards": "awards",
}

_DATE_RANGE_RE = re.compile(
    r"^(?:[A-Za-z]{3,9}\s+)?\d{4}(?:-\d{2})?(?:\s*[–—-]\s*(?:Present|(?:[A-Za-z]{3,9}\s+)?\d{4}(?:-\d{2})?))?$",
    re.I,
)
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def is_linkedin_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == "linkedin.com" or host.endswith(".linkedin.com")


def fetch_url(url: str, *, timeout: float = 15.0) -> tuple[str, str]:
    """Fetch a public URL and return (body_text, content_type)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL must start with http:// or https:// (got {url!r}).")
    if is_linkedin_url(url):
        raise LinkedInAuthwallError(
            "Direct LinkedIn profile URLs are gated behind an authwall (HTTP 999 / login redirect).\n"
            "Instead, export your profile in 2 clicks on LinkedIn:\n"
            "  1. Open your profile -> More -> Save to PDF (Profile.pdf)\n"
            "  2. Run: cvfmt linkedin Profile.pdf --pdf --verify"
        )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "cvfmt/0.1 (+https://github.com/ivans3m/cv-formatter)",
            "Accept": "text/markdown, text/plain, application/json, text/html;q=0.9, */*;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        ctype = resp.headers.get("Content-Type", "").lower()
        raw = resp.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError(f"Response from {url} exceeded {MAX_RESPONSE_BYTES // (1024 * 1024)} MB limit.")
        encoding = resp.headers.get_content_charset() or "utf-8"
        return raw.decode(encoding, errors="replace"), ctype


def convert_json_resume(data: dict, *, paper: str = "a4") -> str:
    """Convert a JSON Resume (https://jsonresume.org/) object into cv-md/1.0."""
    basics = data.get("basics") or {}
    name = (basics.get("name") or "").strip()
    headline = (basics.get("label") or "").strip()
    email = (basics.get("email") or "").strip()
    phone = (basics.get("phone") or "").strip()
    summary = (basics.get("summary") or "").strip()

    loc_obj = basics.get("location") or {}
    loc_parts = [p for p in (loc_obj.get("city"), loc_obj.get("countryCode") or loc_obj.get("region")) if p]
    location = ", ".join(loc_parts)

    links: list[tuple[str, str]] = []
    if basics.get("url"):
        links.append(("Website", str(basics["url"]).strip()))
    for prof in basics.get("profiles") or []:
        u = (prof.get("url") or "").strip()
        net = (prof.get("network") or "Profile").strip()
        if u:
            links.append((net, u))

    positions: list[dict] = []
    for w in data.get("work") or []:
        bullets = list(w.get("highlights") or [])
        if w.get("summary") and not bullets:
            bullets = [str(w["summary"]).strip()]
        positions.append(
            {
                "company": (w.get("name") or w.get("company") or "").strip(),
                "title": (w.get("position") or "").strip(),
                "start": (w.get("startDate") or "").strip(),
                "end": (w.get("endDate") or "").strip() or "Present",
                "location": (w.get("location") or "").strip(),
                "bullets": [str(b).strip() for b in bullets if str(b).strip()],
            }
        )

    education: list[dict] = []
    for ed in data.get("education") or []:
        study = (ed.get("studyType") or "").strip()
        area = (ed.get("area") or "").strip()
        degree = " ".join(p for p in (study, area) if p) or "Education"
        education.append(
            {
                "school": (ed.get("institution") or "").strip(),
                "degree": degree,
                "start": (ed.get("startDate") or "").strip(),
                "end": (ed.get("endDate") or "").strip(),
                "bullets": [],
            }
        )

    skills: list[str] = []
    for sk in data.get("skills") or []:
        kws = sk.get("keywords") or []
        if kws:
            skills.extend(str(k).strip() for k in kws if str(k).strip())
        elif sk.get("name"):
            skills.append(str(sk["name"]).strip())

    languages: list[tuple[str, str]] = []
    for lg in data.get("languages") or []:
        if lg.get("language"):
            languages.append((str(lg["language"]).strip(), str(lg.get("fluency") or "").strip()))

    certifications: list[dict] = []
    for c in data.get("certificates") or []:
        if c.get("name"):
            certifications.append(
                {
                    "name": str(c["name"]).strip(),
                    "authority": str(c.get("issuer") or "").strip(),
                    "date": str(c.get("date") or "").strip(),
                    "url": str(c.get("url") or "").strip(),
                }
            )

    awards: list[dict] = []
    for a in data.get("awards") or []:
        if a.get("title"):
            awards.append(
                {
                    "title": str(a["title"]).strip(),
                    "awarder": str(a.get("awarder") or "").strip(),
                    "date": str(a.get("date") or "").strip(),
                    "summary": str(a.get("summary") or "").strip(),
                }
            )

    volunteering: list[dict] = []
    for v in data.get("volunteer") or []:
        if v.get("organization") or v.get("position"):
            v_bullets = [str(b).strip() for b in (v.get("highlights") or []) if str(b).strip()]
            if v.get("summary") and not v_bullets:
                v_bullets = [str(v["summary"]).strip()]
            volunteering.append(
                {
                    "role": str(v.get("position") or "Volunteer").strip(),
                    "organization": str(v.get("organization") or "").strip(),
                    "start": str(v.get("startDate") or "").strip(),
                    "end": str(v.get("endDate") or "").strip(),
                    "location": "",
                    "bullets": v_bullets,
                }
            )

    interests: list[str] = []
    for item in data.get("interests") or []:
        if isinstance(item, dict) and item.get("name"):
            interests.append(str(item["name"]).strip())
        elif isinstance(item, str) and item.strip():
            interests.append(item.strip())

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
        awards=awards,
        volunteering=volunteering,
        interests=interests,
        paper=paper,
    )


class _CVHtmlExtractor(HTMLParser):
    """Lightweight semantic HTML block & link extractor."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer"}
    BLOCK_TAGS = {"h1", "h2", "h3", "h4", "p", "li", "div", "section", "article", "br", "tr"}

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._in_title = False
        self.title = ""
        self.links: list[tuple[str, str]] = []
        self._cur_href: str | None = None
        self._cur_link_text: list[str] = []
        self._blocks: list[tuple[str, str]] = []
        self._cur_tag = "p"
        self._cur_buf: list[str] = []

    def _flush(self) -> None:
        text = re.sub(r"\s+", " ", unescape("".join(self._cur_buf))).strip()
        self._cur_buf = []
        if text:
            self._blocks.append((self._cur_tag, text))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth > 0:
            return
        if tag == "title":
            self._in_title = True
            return
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self._cur_href = href.strip()
                self._cur_link_text = []
            return
        if tag in self.BLOCK_TAGS:
            self._flush()
            self._cur_tag = tag

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if self._skip_depth > 0:
            return
        if tag == "title":
            self._in_title = False
            return
        if tag == "a" and self._cur_href:
            label = re.sub(r"\s+", " ", "".join(self._cur_link_text)).strip()
            self.links.append((label, self._cur_href))
            self._cur_href = None
            self._cur_link_text = []
            return
        if tag in self.BLOCK_TAGS:
            self._flush()
            self._cur_tag = "p"

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_title:
            self.title += data
            return
        if self._cur_href is not None:
            self._cur_link_text.append(data)
        self._cur_buf.append(data)

    def get_blocks(self) -> list[tuple[str, str]]:
        self._flush()
        return self._blocks


def convert_html_cv(html: str, *, source_url: str = "", paper: str = "a4") -> str:
    """Heuristically convert a public HTML CV webpage into canonical cv-md/1.0."""
    # Prefer <main> or <article> when available to avoid site chrome
    m_main = re.search(r"<main[^>]*>(.*?)</main>", html, re.S | re.I) or re.search(
        r"<article[^>]*>(.*?)</article>", html, re.S | re.I
    )
    scoped_html = m_main.group(1) if m_main else html

    # Also grab page <title> from full HTML for candidate name fallback
    m_title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    page_title = unescape(re.sub(r"\s+", " ", m_title.group(1))).strip() if m_title else ""

    parser = _CVHtmlExtractor()
    parser.feed(scoped_html)
    blocks = parser.get_blocks()

    # Extract email and key links
    email = ""
    links: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    for label, href in parser.links:
        if href.lower().startswith("mailto:"):
            email = href[7:].split("?")[0].strip()
        elif href.startswith(("http://", "https://")):
            low = href.lower()
            if "linkedin.com/in/" in low and href not in seen_urls:
                links.append(("LinkedIn", href))
                seen_urls.add(href)
            elif "github.com/" in low and href not in seen_urls:
                links.append(("GitHub", href))
                seen_urls.add(href)

    if source_url:
        parsed_src = urlparse(source_url)
        site_root = f"{parsed_src.scheme}://{parsed_src.netloc}"
        if site_root not in seen_urls:
            links.insert(0, ("Website", site_root))

    if not email:
        m_em = _EMAIL_RE.search(" ".join(t for _, t in blocks))
        if m_em:
            email = m_em.group(0)

    # Bucket blocks by canonical section
    sections: dict[str, list[tuple[str, str]]] = {}
    cur_sec: str | None = None
    header_texts: list[str] = []

    for tag, text in blocks:
        if text in ("*", "•", "—", "–"):
            continue
        norm_heading = " ".join(text.replace("\u2019", "'").replace("\u2018", "'").lower().rstrip(":").split())
        sec_key = _SECTION_ALIASES.get(norm_heading)
        is_heading_tag = tag in ("h1", "h2", "h3", "h4")
        if sec_key and (is_heading_tag or (sec_key in _CORE_HTML_SECTIONS and len(text) <= 24)):
            cur_sec = sec_key
            sections.setdefault(cur_sec, [])
            continue
        if cur_sec is None:
            header_texts.append(text)
        else:
            sections[cur_sec].append((tag, text))

    # Infer candidate name from header or <title> (e.g. "CV – courtesy of Ivan Diuldia")
    name = ""
    for ht in header_texts:
        if ht.lower() not in ("cv", "resume", "curriculum vitae") and len(ht) <= 60:
            name = ht
            break
    if not name and page_title:
        cleaned_title = re.sub(r"^(?:CV|Resume|Curriculum Vitae)\s*[–—\-|:]\s*", "", page_title, flags=re.I)
        cleaned_title = re.sub(r"^courtesy of\s+", "", cleaned_title, flags=re.I)
        cleaned_title = re.sub(r"\s*[–—\-|:]\s*(?:CV|Resume).*$", "", cleaned_title, flags=re.I)
        name = cleaned_title.strip()

    # Summary
    summary_lines = [t for _, t in sections.get("summary", []) if not t.startswith("–") and len(t) > 15]
    summary = " ".join(summary_lines[:2])

    # Experience: split entries on lines containing ' @ ' or ' — ' or preceding a date range line
    exp_blocks = sections.get("experience", [])
    positions: list[dict] = []
    i = 0
    while i < len(exp_blocks):
        tag, text = exp_blocks[i]
        next_is_date = i + 1 < len(exp_blocks) and bool(_DATE_RANGE_RE.match(exp_blocks[i + 1][1]))
        is_role_header = (" @ " in text) or next_is_date or (tag in ("h3", "h4") and len(text) < 100)
        if is_role_header:
            if " @ " in text:
                title, company = [p.strip() for p in text.split(" @ ", 1)]
            elif " — " in text:
                title, company = [p.strip() for p in text.split(" — ", 1)]
            else:
                title, company = text, ""
            pos = {"title": title, "company": company, "start": "", "end": "Present", "location": "", "bullets": []}
            i += 1
            if i < len(exp_blocks) and _DATE_RANGE_RE.match(exp_blocks[i][1]):
                d_raw = exp_blocks[i][1].strip()
                if re.search(r"\s+[–—-]\s+", d_raw):
                    parts = re.split(r"\s+[–—-]\s+", d_raw, maxsplit=1)
                    pos["start"], pos["end"] = parts[0].strip(), parts[1].strip()
                elif re.match(r"^\d{4}\s*[–—-]\s*(?:Present|\d{4})$", d_raw, re.I):
                    parts = re.split(r"\s*[–—-]\s*", d_raw, maxsplit=1)
                    pos["start"], pos["end"] = parts[0].strip(), parts[1].strip()
                else:
                    pos["start"], pos["end"] = d_raw, d_raw
                i += 1
            if i < len(exp_blocks) and len(exp_blocks[i][1]) < 60 and "," in exp_blocks[i][1] and not exp_blocks[i][1].endswith("."):
                pos["location"] = exp_blocks[i][1]
                i += 1
            positions.append(pos)
        else:
            if positions and len(text) > 10:
                positions[-1]["bullets"].append(text)
            i += 1

    # Education
    edu_blocks = sections.get("education", [])
    education: list[dict] = []
    j = 0
    while j < len(edu_blocks):
        _, school = edu_blocks[j]
        degree, start_e, end_e = "Education", "", ""
        if j + 1 < len(edu_blocks):
            nxt = edu_blocks[j + 1][1]
            m_ed = re.match(r"^(\d{4})\s*[–—-]\s*(\d{4})\s*[–—-]\s*(.+)$", nxt)
            if m_ed:
                start_e, end_e, degree = m_ed.group(1), m_ed.group(2), m_ed.group(3).strip()
                j += 2
                if j < len(edu_blocks) and len(edu_blocks[j][1]) < 50 and "," in edu_blocks[j][1]:
                    j += 1
                education.append({"school": school, "degree": degree, "start": start_e, "end": end_e, "bullets": []})
                continue
        education.append({"school": school, "degree": degree, "start": start_e, "end": end_e, "bullets": []})
        j += 1

    # Skills (skip prose/footnote paragraphs that end with a period)
    skills: list[str] = []
    for _, t in sections.get("skills", []):
        if t.lower().startswith("in no particular order"):
            continue
        if t.endswith(".") or t.lower().startswith(("contact", "email")):
            break
        if "," in t:
            skills.extend(item.strip() for item in t.split(",") if item.strip() and len(item.strip()) <= 60)
        elif len(t) <= 40:
            skills.append(t)

    # Optional HTML sections (languages, certifications, awards, courses, interests)
    languages: list[tuple[str, str]] = []
    for _, t in sections.get("languages", []):
        if ":" in t:
            lang_name, lvl = t.split(":", 1)
            if lang_name.strip():
                languages.append((lang_name.strip(), lvl.strip()))
        elif len(t) <= 60:
            languages.append((t, ""))

    certifications = [
        {"name": t, "authority": "", "date": ""}
        for _, t in sections.get("certifications", [])
        if len(t) > 2
    ]
    awards = [
        {"title": t, "awarder": "", "date": "", "summary": ""}
        for _, t in sections.get("awards", [])
        if len(t) > 2
    ]
    courses = [
        {"name": t, "provider": "", "date": ""}
        for _, t in sections.get("courses", [])
        if len(t) > 2
    ]
    interests: list[str] = []
    for _, t in sections.get("interests", []):
        if "," in t:
            interests.extend(item.strip() for item in t.split(",") if item.strip() and len(item.strip()) <= 60)
        elif len(t) <= 60:
            interests.append(t)

    # Infer location from most recent experience if available
    location = next((p["location"] for p in positions if p.get("location")), "")

    return _build_cv_markdown(
        name=name,
        location=location,
        email=email,
        links=links,
        summary=summary,
        positions=positions,
        education=education,
        skills=skills,
        languages=languages,
        certifications=certifications,
        awards=awards,
        courses=courses,
        interests=interests,
        paper=paper,
    )


def import_from_url(url: str, *, paper: str = "a4") -> str:
    """Fetch a public CV URL (cv-md/1.0, JSON Resume, or HTML page) and return cv-md/1.0 text."""
    body, ctype = fetch_url(url)
    stripped = body.lstrip()

    # 1. Raw cv-md/1.x Markdown
    schema_alt = "|".join(re.escape(s) for s in SUPPORTED_SCHEMAS)
    if stripped.startswith("---") and re.search(
        rf'schema:\s*["\']?(?:{schema_alt})["\']?(?:\s|$)', stripped[:400]
    ):
        return body

    # 2. JSON Resume
    if "json" in ctype or stripped.startswith("{"):
        try:
            data = json.loads(stripped)
            if isinstance(data, dict) and ("basics" in data or "work" in data):
                return convert_json_resume(data, paper=paper)
        except json.JSONDecodeError:
            pass

    # 3. Public HTML CV page
    return convert_html_cv(body, source_url=url, paper=paper)
