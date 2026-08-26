"""Run all supplementary academic audits and write one report."""

from __future__ import annotations

import json
from pathlib import Path

from .case_audit import audit as audit_cases
from .fault_gate_audit import audit as audit_fault_gate
from .independence_audit import audit as audit_independence
from .layer_readiness import audit as audit_layers
from .metric_audit import audit as audit_metrics
from .path_contribution_audit import audit as audit_path_contribution
from .paths import PACKAGE_ROOT
from .readiness_figure import draw as draw_readiness
from .retrieval_failure_audit import audit as audit_retrieval_failure


OUT = PACKAGE_ROOT / "outputs"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "veriquery-academic-extension-1",
        "metric_consistency": audit_metrics(),
        "case_construction": audit_cases(),
        "fault_gate_response": audit_fault_gate(),
        "independence": audit_independence(),
        "layer_readiness": audit_layers(),
        "path_contribution": audit_path_contribution(),
        "retrieval_rank_displacement": audit_retrieval_failure(),
        "related_work_matrix": "academic_extension/related_work_matrix.json",
        "scope": "Supplementary structural audits over frozen artifacts; no model, network, expert, or user data.",
    }
    path = OUT / "academic_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    draw_readiness()
    print(path)


if __name__ == "__main__":
    main()
