"""Aspirational bullet validation."""

from __future__ import annotations

from cvfmt.parser import parse_cv_text
from cvfmt.validator import validate_cv


def test_aspirational_error_in_strict_cv() -> None:
    md = """---
schema: cv-md/1.1
name: Alex Dev
email: alex@example.com
---

## Experience

### Engineer — Acme
*2023-01 – Present | Berlin, Germany*

- **(Aspirational)** Scaled platform to 10M users (not yet verified).

## Skills

- **Core:** Python

## Languages

- **English:** C2
"""
    doc = parse_cv_text(md)
    val = validate_cv(doc)
    assert not val.ok
    assert any(e.code == "ASPIRATIONAL_IN_STRICT" for e in val.errors)


def test_aspirational_warning_in_dreamer_cv() -> None:
    md = """---
schema: cv-md/1.1
name: Alex Dev
email: alex@example.com
tailor_mode: dreamer
---

## Experience

### Engineer — Acme
*2023-01 – Present | Berlin, Germany*

- **(Aspirational)** Scaled platform to 10M users.

## Skills

- **Core:** Python

## Languages

- **English:** C2
"""
    doc = parse_cv_text(md)
    val = validate_cv(doc)
    assert val.ok
    assert any(w.code == "ASPIRATIONAL_BULLET" for w in val.warnings)

    # --allow-aspirational suppresses warnings only on dreamer CVs
    val_allowed = validate_cv(doc, allow_aspirational=True)
    assert val_allowed.ok
    assert not any(w.code == "ASPIRATIONAL_BULLET" for w in val_allowed.warnings)


def test_allow_aspirational_does_not_bypass_strict_error() -> None:
    md = """---
schema: cv-md/1.1
name: Alex Dev
email: alex@example.com
tailor_mode: strict
---

## Experience

### Engineer — Acme
*2023-01 – Present | Berlin, Germany*

- **(aspirational)** Scaled platform to 10M users.

## Skills

- **Core:** Python

## Languages

- **English:** C2
"""
    doc = parse_cv_text(md)
    val = validate_cv(doc, allow_aspirational=True)
    assert not val.ok
    assert any(e.code == "ASPIRATIONAL_IN_STRICT" for e in val.errors)