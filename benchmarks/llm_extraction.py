"""LLM Structured Extraction Benchmark for cvfmt PDFs.

Renders cv-md/1.0 golden fixtures to PDF, extracts the raw text layer (simulating
an AI recruiter screening pipeline), exports extraction prompts, and grades any
LLM's structured JSON output against ground truth parsed from the source Markdown.

Usage:
    # 1. Render fixtures to PDF, dump raw extracted texts & ground truth
    .venv/bin/python benchmarks/llm_extraction.py prepare --out /tmp/cvfmt-bench

    # 2. Grade a predictions.json file against ground truth
    .venv/bin/python benchmarks/llm_extraction.py grade --bench-dir /tmp/cvfmt-bench --predictions /tmp/cvfmt-bench/predictions.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pdfplumber

from cvfmt.models import CVDocument
from cvfmt.parser import parse_cv_file
from cvfmt.renderer import compile_pdf
from cvfmt.typst_gen import format_date_range


FIXTURES_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
METRIC_RE = re.compile(r"(?:€|\$|£)?\d+(?:[.,]\d+)?(?:%|K|M|B|x|ms|s|/month|/year|/hour|/day|/sec)?(?:\+|x)?")


def _norm(s: str | None) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip().lower()


def _extract_metrics_from_doc(doc: CVDocument) -> list[str]:
    """Extract high-signal quantified metrics (currency, %, latency, scale) from Experience/Projects."""
    chunks: list[str] = []
    for sec in doc.sections:
        if sec.title.lower() in ("experience", "projects"):
            for e in sec.entries:
                chunks.extend(e.bullets)
                for sr in e.sub_roles:
                    chunks.extend(sr.bullets)
    text = "\n".join(chunks)
    # Capture meaningful metrics (with units, currency, %, +, or >= 2 digits)
    found = re.findall(
        r"(?:[€$£]\d+(?:[.,]\d+)?[KMB]?|\b\d+(?:[.,]\d+)?%|\b\d+(?:[.,]\d+)?(?:ms|x)\b|\b\d+(?:,\d{3})+\+?|\b\d+(?:\.\d+)?[KMB]\+?)",
        text,
    )
    # Deduplicate preserving order
    seen: set[str] = set()
    out: list[str] = []
    for m in found:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def build_ground_truth(doc: CVDocument) -> dict:
    """Build structured ground truth from the canonical cv-md/1.0 source."""
    fm = doc.frontmatter
    roles: list[dict] = []
    education: list[dict] = []
    languages: list[dict] = []

    for sec in doc.sections:
        sec_l = sec.title.lower()
        if sec_l == "experience":
            for e in sec.entries:
                if e.sub_roles:
                    company = e.primary
                    for sr in e.sub_roles:
                        roles.append(
                            {
                                "title": sr.title,
                                "company": company,
                                "date_range": format_date_range(sr.date_range or ""),
                            }
                        )
                else:
                    roles.append(
                        {
                            "title": e.primary,
                            "company": e.secondary or "",
                            "date_range": format_date_range(e.date_range or ""),
                        }
                    )
        elif sec_l == "education":
            for e in sec.entries:
                education.append(
                    {
                        "degree": e.primary,
                        "institution": e.secondary or "",
                        "date_range": format_date_range(e.date_range or ""),
                    }
                )
        elif sec_l == "languages":
            for b in sec.bullets:
                m = re.match(r"^\*\*([^:*]+):?\*\*:?\s*(.+)$", b)
                if m:
                    lang_name = m.group(1).strip()
                    lvl_m = re.search(r"\b(A1|A2|B1|B2|C1|C2|Native)\b", m.group(2), re.I)
                    languages.append(
                        {
                            "language": lang_name,
                            "level": lvl_m.group(1) if lvl_m else m.group(2).strip(),
                        }
                    )

    return {
        "name": fm.name,
        "email": fm.email,
        "location": fm.location or "",
        "work_authorization": fm.work_authorization or "",
        "roles": roles,
        "education": education,
        "languages": languages,
        "metrics": _extract_metrics_from_doc(doc),
    }


def extract_pdf_text(pdf_path: Path) -> str:
    chunks: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            chunks.append(page.extract_text() or "")
    return "\n\n".join(chunks).strip()


def prepare(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle: dict[str, dict] = {}
    for md_path in sorted(FIXTURES_DIR.glob("*.md")):
        doc = parse_cv_file(md_path)
        pdf_path = out_dir / f"{md_path.stem}.pdf"
        compile_pdf(doc, pdf_path)
        raw_text = extract_pdf_text(pdf_path)
        (out_dir / f"{md_path.stem}.txt").write_text(raw_text, encoding="utf-8")
        bundle[md_path.stem] = {
            "fixture": md_path.name,
            "ground_truth": build_ground_truth(doc),
            "extracted_text": raw_text,
        }

    (out_dir / "ground_truth.json").write_text(
        json.dumps({k: v["ground_truth"] for k, v in bundle.items()}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return bundle


def grade_fixture(gt: dict, pred: dict) -> dict:
    # 1. Identity fields (name, email, location, work_authorization)
    id_fields = ("name", "email", "location", "work_authorization")
    id_hits = sum(1 for f in id_fields if _norm(gt.get(f)) == _norm(pred.get(f)))
    id_score = id_hits / len(id_fields)

    # 2. Roles (title, company, date_range)
    gt_roles = gt.get("roles", [])
    pred_roles = pred.get("roles", [])
    role_matches = 0
    date_matches = 0
    for gr in gt_roles:
        matched_role = any(
            _norm(gr["title"]) == _norm(pr.get("title"))
            and _norm(gr["company"]) == _norm(pr.get("company"))
            for pr in pred_roles
        )
        matched_date = any(
            _norm(gr["title"]) == _norm(pr.get("title"))
            and _norm(gr["date_range"]).replace("-", "–") == _norm(pr.get("date_range")).replace("-", "–")
            for pr in pred_roles
        )
        if matched_role:
            role_matches += 1
        if matched_date:
            date_matches += 1

    role_score = role_matches / len(gt_roles) if gt_roles else 1.0
    date_score = date_matches / len(gt_roles) if gt_roles else 1.0

    # 3. Languages + CEFR level
    gt_langs = gt.get("languages", [])
    pred_langs = pred.get("languages", [])
    lang_hits = sum(
        1
        for gl in gt_langs
        if any(
            _norm(gl["language"]) == _norm(pl.get("language"))
            and _norm(gl["level"]) in _norm(pl.get("level"))
            for pl in pred_langs
        )
    )
    lang_score = lang_hits / len(gt_langs) if gt_langs else 1.0

    # 4. Education (institution)
    gt_edu = gt.get("education", [])
    pred_edu = pred.get("education", [])
    edu_hits = sum(
        1
        for ge in gt_edu
        if any(_norm(ge["institution"]) == _norm(pe.get("institution")) for pe in pred_edu)
    )
    edu_score = edu_hits / len(gt_edu) if gt_edu else 1.0

    # 5. Metrics recall
    gt_metrics = gt.get("metrics", [])
    pred_metrics_blob = " ".join(str(m) for m in pred.get("metrics", []))
    metric_hits = sum(1 for m in gt_metrics if m in pred_metrics_blob)
    metric_recall = metric_hits / len(gt_metrics) if gt_metrics else 1.0

    overall = (id_score + role_score + date_score + lang_score + edu_score + metric_recall) / 6.0
    return {
        "identity": round(id_score * 100, 1),
        "roles": round(role_score * 100, 1),
        "dates": round(date_score * 100, 1),
        "languages": round(lang_score * 100, 1),
        "education": round(edu_score * 100, 1),
        "metrics_recall": round(metric_recall * 100, 1),
        "overall": round(overall * 100, 1),
        "counts": {
            "roles": f"{role_matches}/{len(gt_roles)}",
            "dates": f"{date_matches}/{len(gt_roles)}",
            "languages": f"{lang_hits}/{len(gt_langs)}",
            "education": f"{edu_hits}/{len(gt_edu)}",
            "metrics": f"{metric_hits}/{len(gt_metrics)}",
        },
    }


def grade_all(bench_dir: Path, predictions_path: Path) -> dict:
    gt_all = json.loads((bench_dir / "ground_truth.json").read_text(encoding="utf-8"))
    pred_all = json.loads(predictions_path.read_text(encoding="utf-8"))
    results = {}
    for key, gt in gt_all.items():
        results[key] = grade_fixture(gt, pred_all.get(key, {}))
    avg = round(sum(r["overall"] for r in results.values()) / len(results), 1) if results else 0.0
    summary = {"fixtures": results, "average_overall": avg}
    (bench_dir / "report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="cvfmt LLM structured extraction benchmark")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prep = sub.add_parser("prepare")
    p_prep.add_argument("--out", type=Path, required=True)

    p_grade = sub.add_parser("grade")
    p_grade.add_argument("--bench-dir", type=Path, required=True)
    p_grade.add_argument("--predictions", type=Path, required=True)

    args = parser.parse_args()
    if args.cmd == "prepare":
        bundle = prepare(args.out)
        print(f"Prepared {len(bundle)} fixtures in {args.out}: {list(bundle.keys())}")
    elif args.cmd == "grade":
        summary = grade_all(args.bench_dir, args.predictions)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
