"""Write prompt bundle for external LLM dreamer tailoring."""

from __future__ import annotations

from pathlib import Path

from cvfmt.models import CVDocument
from cvfmt.writer import document_to_markdown


PROMPT_TEMPLATE = """# CV tailor — dreamer bundle

Use the cv-tailor dreamer contract:

1. Read `base.md` (master cv-md) and `jd.txt` (target job).
2. Produce a 1–2 page tailored cv-md/1.1 file with `tailor_mode: dreamer`.
3. Never invent metrics in unmarked bullets; prefix imagined claims with **(Aspirational)** .
4. Carry forward `## Facts`; park trimmed items under `### Archived for <target>`.
5. Output valid cv-md only (YAML frontmatter + canonical ## sections).

Target label for archiving: {target}
"""


def write_prepare_bundle(
    doc: CVDocument,
    jd_text: str,
    out_dir: Path,
    *,
    tailor_target: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "jd.txt").write_text(jd_text.strip() + "\n", encoding="utf-8")
    (out_dir / "base.md").write_text(document_to_markdown(doc), encoding="utf-8")
    (out_dir / "prompt.md").write_text(
        PROMPT_TEMPLATE.replace("{target}", tailor_target),
        encoding="utf-8",
    )