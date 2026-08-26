"""Compute structural readiness of ERC evidence for the four rule layers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .paths import project_root

ROOT = project_root()
CASE_FILE = ROOT / "research" / "outputs" / "public-erc" / "expanded-62.jsonl"

LAYER_REQUIREMENTS = {
    "L1_static_logic": ("driver.VOH", "driver.VOL", "receiver.VIH", "receiver.VIL"),
    "L2_signal_integrity": ("trace_length_mm", "line_impedance_ohm", "source_impedance_ohm"),
    "L3_topology": ("topology.driver_interface", "topology.receiver_interface", "topology.driver_direction", "topology.receiver_direction"),
    "L4_environment": ("environment.temperature_c", "environment.vcc_v", "environment.drift_coefficient"),
}


def _available(row: dict[str, Any], requirement: str) -> bool:
    if requirement.startswith("topology."):
        return requirement.split(".", 1)[1] in row.get("topology", {})
    if requirement.startswith("environment."):
        return requirement.split(".", 1)[1] in row.get("environment", {})
    return requirement in row.get("evidence_bindings", {}) and row.get("evidence_bindings", {}).get(requirement) is not None


def audit() -> dict[str, Any]:
    rows = [json.loads(line) for line in CASE_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    per_case = []
    counts = Counter()
    missing = Counter()
    for row in rows:
        available_layers = []
        for layer, requirements in LAYER_REQUIREMENTS.items():
            absent = [item for item in requirements if not _available(row, item)]
            if not absent:
                available_layers.append(layer)
            else:
                missing.update((layer, item) for item in absent)
        counts.update(available_layers)
        per_case.append({"id": row["id"], "available_layers": available_layers})
    return {
        "case_count": len(rows),
        "layer_requirements": LAYER_REQUIREMENTS,
        "cases_with_all_requirements": dict(sorted(counts.items())),
        "missing_requirement_counts": {f"{layer}:{field}": count for (layer, field), count in sorted(missing.items())},
        "per_case": per_case,
        "interpretation": "Readiness profile only. It identifies whether a case contains prerequisites for a layer; it is not a layer-wise accuracy or ablation result.",
    }
