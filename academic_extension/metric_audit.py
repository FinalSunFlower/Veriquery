"""Audit consistency between manuscript claims and frozen metric JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .paths import project_root

ROOT = project_root()
PAPER = ROOT / "tmlr_paper" / "main.tex"
REPORT = ROOT / "research" / "outputs" / "tmlr" / "benchmark_report.json"


def _report() -> dict[str, Any]:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def _contains_number(text: str, value: float) -> bool:
    token = f"{value:.4f}"
    return token in text or f"{value:.3f}" in text or f"{value:.2f}" in text


def audit() -> dict[str, Any]:
    text = PAPER.read_text(encoding="utf-8")
    report = _report()["claims"]
    expected = {
        "qasper_rrf_ndcg10": report["retrieval"]["bm25_dense_rrf_ndcg10"],
        "qasper_full_hybrid_ndcg10": report["retrieval"]["full_hybrid_ndcg10"],
        "condition_exact_recovery": report["evidence_state"]["adaptive_condition_exact_fact_recovery"],
        "condition_page_accuracy": report["evidence_state"]["adaptive_condition_citation_page_accuracy"],
        "condition_coordinate_rate": report["evidence_state"]["adaptive_condition_value_span_coordinate_rate"],
        "public_30_guided_accuracy": report["public_erc"]["primary_30"]["document_guided_accuracy"],
        "public_30_guided_false_safe": report["public_erc"]["primary_30"]["document_guided_false_safe_rate"],
        "public_62_guided_accuracy": report["public_erc"]["expanded_62"]["document_guided_accuracy"],
        "public_62_guided_false_safe": report["public_erc"]["expanded_62"]["document_guided_false_safe_rate"],
    }
    checks = {name: _contains_number(text, value) for name, value in expected.items()}
    semantic_checks = {
        "exact_fact_recovery_rate_label": "exact fact recovery rate" in text,
        "coordinate_coverage_label": "value-span coordinate coverage" in text,
        "multifault_three_severity_sequence": "0.6333, 0.3333, and 0.0000" in text,
        "formal_contract_source_boundary": "source-constrained formal contracts derived from public manufacturer documents" in text,
        "canonical_evaluation_boundary": "documentary and formal contract evaluations, not expert, physical-safety, field, or user studies" in text,
    }
    stale = {
        "old_exact_recovery_0.6786": "0.6786" in text,
        "old_pages_1.2143": "1.2143" in text,
        "old_pages_1.21": bool(re.search(r"1\.21(?!\d)", text)),
    }
    return {
        "paper": str(PAPER.relative_to(ROOT)).replace("\\", "/"),
        "report": str(REPORT.relative_to(ROOT)).replace("\\", "/"),
        "expected_values": expected,
        "presence_checks": checks,
        "all_key_values_present": all(checks.values()),
        "semantic_checks": semantic_checks,
        "all_semantic_checks_pass": all(semantic_checks.values()),
        "stale_draft_value_checks": stale,
        "no_stale_draft_values": not any(stale.values()),
        "interpretation": "Consistency audit only; it does not validate the underlying benchmarks.",
    }
