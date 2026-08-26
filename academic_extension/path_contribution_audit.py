"""Audit which retrieval-path contributions are identifiable from frozen data.

The QASPER release stores final ranked passage IDs and aggregate metrics, but
not candidate-level path provenance or a replayable QASPER hybrid runner. This
module reports the exact contrasts that are identifiable and emits an explicit
missingness record for individual path leave-one-out estimates.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import project_root


ROOT = project_root()
BASE = ROOT / "research" / "outputs" / "qasper-v0.3"


def _metrics(name: str) -> dict[str, float]:
    payload = json.loads((BASE / "metrics" / f"{name}.json").read_text(encoding="utf-8"))
    return {key: float(value) for key, value in payload["metrics"].items()}


def audit() -> dict[str, Any]:
    bm25 = _metrics("bm25")
    rrf = _metrics("bm25_dense_rrf")
    full = _metrics("full_hybrid")
    contrasts = {
        "dense_plus_bm25_increment_over_bm25": {
            "ndcg10": rrf["ndcg@10"] - bm25["ndcg@10"],
            "recall10": rrf["recall@10"] - bm25["recall@10"],
        },
        "all_extra_paths_increment_over_bm25_dense_rrf": {
            "ndcg10": full["ndcg@10"] - rrf["ndcg@10"],
            "recall10": full["recall@10"] - rrf["recall@10"],
        },
        "full_hybrid_increment_over_bm25": {
            "ndcg10": full["ndcg@10"] - bm25["ndcg@10"],
            "recall10": full["recall@10"] - bm25["recall@10"],
        },
    }
    unavailable = {
        path: {
            "leave_one_out_estimable": False,
            "reason": "frozen QASPER records omit candidate path provenance and no replayable QASPER runner is released",
        }
        for path in ("condition_aware", "structured", "table")
    }
    return {
        "dataset": "QASPER v0.3",
        "variant_metrics": {
            "bm25": bm25,
            "bm25_dense_rrf": rrf,
            "full_hybrid": full,
        },
        "identifiable_contrasts": contrasts,
        "individual_path_leave_one_out": unavailable,
        "identifiability": {
            "candidate_path_provenance_retained": False,
            "replayable_qasper_runner_available": False,
            "aggregate_extra_path_effect_identifiable": True,
            "individual_extra_path_effects_identifiable": False,
        },
        "interpretation": (
            "The negative full-hybrid contrast is an aggregate effect of all paths added beyond BM25+dense RRF. "
            "It cannot be allocated to condition-aware, structured, or table retrieval without rerunning the "
            "benchmark with per-candidate provenance and matched leave-one-out variants."
        ),
    }
