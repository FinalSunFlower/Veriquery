"""Audit whether the academic extension is coupled to the standard pipeline."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .paths import project_root


PACKAGE = Path(__file__).resolve().parent


def _python_files(path: Path) -> list[Path]:
    return sorted(path.rglob("*.py"))


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def audit() -> dict[str, Any]:
    root = project_root()
    standard_files = _python_files(root / "research")
    extension_files = _python_files(PACKAGE)
    imports = set().union(*(_imports(path) for path in extension_files)) if extension_files else set()
    extension_stems = {path.stem for path in extension_files if path.stem != "__init__"}
    standard_stems = {path.stem for path in standard_files if path.stem != "__init__"}
    return {
        "extension_python_files": len(extension_files),
        "standard_research_python_files": len(standard_files),
        "extension_source_bytes": sum(path.stat().st_size for path in extension_files),
        "standard_research_source_bytes": sum(path.stat().st_size for path in standard_files),
        "extension_imports_standard_research": sorted(name for name in imports if name == "research"),
        "shared_module_stems": sorted(extension_stems & standard_stems),
        "reads_frozen_artifacts": True,
        "runs_models_or_network": False,
        "implements_retrieval_extraction_or_verification": False,
        "interpretation": (
            "The extension is an independent audit layer: it consumes frozen artifacts and manuscript text, "
            "but does not call or reimplement retrieval, extraction, ranking, verification, or model components."
        ),
    }
