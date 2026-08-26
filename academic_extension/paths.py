"""Locate the full workspace or the self-contained academic input snapshot."""

from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent


def project_root() -> Path:
    """Return a root containing ``tmlr_paper`` and frozen ``research`` inputs."""

    repository_root = PACKAGE_ROOT.parent
    candidates = (
        repository_root,
        repository_root.parent,
        PACKAGE_ROOT / "bundle_inputs",
        repository_root / "zenodo_preprint" / "artifact" / "academic_extension" / "bundle_inputs",
    )
    for candidate in candidates:
        if (candidate / "tmlr_paper" / "main.tex").is_file() and (
            candidate / "research" / "outputs" / "tmlr" / "benchmark_report.json"
        ).is_file():
            return candidate
    raise FileNotFoundError(
        "VeriQuery inputs not found. Run inside tmlr_workspace or keep bundle_inputs/ next to the package."
    )
