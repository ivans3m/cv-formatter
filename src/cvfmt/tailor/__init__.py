"""Role-tailoring helpers for cv-md master CVs."""

from cvfmt.tailor.coverage import coverage_report
from cvfmt.tailor.pipeline_strict import tailor_strict
from cvfmt.tailor.prepare import write_prepare_bundle

__all__ = ["coverage_report", "tailor_strict", "write_prepare_bundle"]