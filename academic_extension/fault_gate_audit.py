"""Summarize fault-type behavior of the frozen ERC evidence gate.

This is a gate-response audit over synthetic invalidated bindings.  It is not
a leave-one-rule-layer-out evaluation and does not claim electrical accuracy.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .paths import project_root


ROOT = project_root()
MANIFEST = ROOT / "research" / "outputs" / "public-erc" / "multifault-stress" / "run_manifest.json"

FAULT_PATHS = {
    "missing_source": ("receiver.VIH", "topology.receiver_direction"),
    "condition_mismatch": ("receiver.VIH", "topology.driver_interface"),
    "unit_or_bound_flip": ("driver.VOH", "receiver.VIL"),
    "page_or_anchor_noise": ("receiver.VIH", "topology.receiver_interface"),
    "conflicting_candidates": ("receiver.VIH", "topology.driver_direction"),
}


def _activated_count(severity: int, fault: str) -> int | None:
    """Count activated cases from the frozen prediction rows, not a surrogate hash."""
    prediction_dir = MANIFEST.parent / "predictions"
    # The release snapshot historically used JSON files while the workspace
    # uses JSONL. Accept both layouts so the audit is reproducible from either.
    candidates = (
        prediction_dir / f"{fault}-s{severity}-evidence_gate.jsonl",
        prediction_dir / f"{fault}-s{severity}-evidence_gate.json",
    )
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        return None
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("rows", payload.get("predictions", []))
    return sum(bool(row.get("faulted_paths")) for row in rows)


def _metrics(level: Mapping[str, Any], variant: str) -> dict[str, float]:
    metric = level["variants"][variant]["metrics"]
    return {
        "coverage": float(metric["decision_coverage"]),
        "abstention": float(metric["abstention_rate"]),
        "false_safe": float(metric["false_safe_rate"]),
    }


def audit() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    for fault in manifest["fault_types"]:
        rows[fault] = {}
        for severity in (1, 2, 3):
            level = manifest["matrix"][fault][str(severity)]
            rows[fault][str(severity)] = {
                "evidence_gate": _metrics(level, "evidence_gate"),
                "voltage_only": _metrics(level, "voltage_only"),
            }
    return {
        "case_count_per_fault_and_severity": int(manifest["case_count"]),
        "fault_types": list(manifest["fault_types"]),
        "severity_rule": manifest["severity_rule"],
        "fault_paths": {fault: list(paths) for fault, paths in FAULT_PATHS.items()},
        "activated_case_counts": {
            fault: {str(severity): _activated_count(severity, fault) for severity in (1, 2, 3)}
            for fault in manifest["fault_types"]
        },
        "zero_event_95_upper_bound_per_cell": 1.0 - 0.05 ** (1.0 / int(manifest["case_count"])),
        "responses": rows,
        "all_gate_false_safe_zero": all(
            values[severity]["evidence_gate"]["false_safe"] == 0.0
            for values in rows.values()
            for severity in values
        ),
        "interpretation": (
            "Each injected type invalidates a declared documentary binding. Equal trajectories across types "
            "reflect the shared deterministic activation rule and fail-closed gate, not equal real-world error "
            "rates or layer-wise rule contribution."
        ),
    }
