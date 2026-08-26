"""Audit the construction and stratification of public formal ERC cases."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .paths import project_root

ROOT = project_root()
BASE = ROOT / "research" / "outputs" / "public-erc"


def _rows(name: str) -> list[dict[str, Any]]:
    path = BASE / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _mechanism(row: dict[str, Any]) -> str:
    explicit = row.get("formal_model_kind")
    if explicit == "st_i2c_clock_filter_budget":
        return "ST I2C timing/filter"
    if explicit == "i2c_pullup_interval":
        return "I2C pull-up interval"
    if explicit == "microchip_can_termination":
        return "CAN termination topology"
    topology = row.get("topology", {})
    if "floating_time_ns" in topology or "driver_mode" in topology:
        return "CMOS floating/pull-up"
    return "unclassified"


def _suite(rows: list[dict[str, Any]]) -> dict[str, Any]:
    documents = Counter(
        source.get("document_id")
        for row in rows
        for source in row.get("sources", [])
        if source.get("document_id")
    )
    return {
        "case_count": len(rows),
        "mechanisms": dict(sorted(Counter(_mechanism(row) for row in rows).items())),
        "labels": dict(sorted(Counter(row.get("reference_label") for row in rows).items())),
        "reference_types": dict(sorted(Counter(row.get("reference_type") for row in rows).items())),
        "source_document_mentions": dict(sorted(documents.items())),
        "split": dict(sorted(Counter(row.get("split") for row in rows).items())),
        "configuration_hashes": len({row.get("external_artifact", {}).get("configuration_sha256") for row in rows}),
    }


def audit() -> dict[str, Any]:
    sensitivity = json.loads((BASE / "expanded-62.sensitivity.json").read_text(encoding="utf-8"))
    margins = [float(item["signed_margin"]) for item in sensitivity["cases"] if item.get("signed_margin") is not None]
    missing_margin_count = len(sensitivity["cases"]) - len(margins)
    fault_files = sorted((BASE / "multifault-stress" / "metrics").glob("*-s[1-3]-evidence_gate.json"))
    faults = Counter()
    severities = Counter()
    for path in fault_files:
        stem = path.name.removesuffix("-evidence_gate.json")
        fault, severity = stem.rsplit("-s", 1)
        faults[fault] += 1
        severities[int(severity)] += 1
    return {
        "primary_30": _suite(_rows("combined.jsonl")),
        "expanded_62": _suite(_rows("expanded-62.jsonl")),
        "boundary_margin": {
            "case_count": len(margins),
            "missing_margin_count": missing_margin_count,
            "min": min(margins),
            "max": max(margins),
            "exact_boundary_count": sum(abs(value) < 1e-9 for value in margins),
            "near_boundary_abs_le_1": sum(abs(value) <= 1.0 for value in margins),
            "positive_margin_count": sum(value > 0 for value in margins),
            "negative_margin_count": sum(value < 0 for value in margins),
        },
        "multifault_metric_files": {
            "fault_types": dict(sorted(faults.items())),
            "severity_file_counts": dict(sorted(severities.items())),
            "expected_fault_types": 5,
            "expected_nonzero_severities": 3,
        },
        "interpretation": "These are source-constrained formal contracts, stratified by mechanism and boundary distance; they are not open-world or prevalence samples.",
    }
