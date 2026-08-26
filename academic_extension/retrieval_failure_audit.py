"""Audit the frozen full-hybrid versus RRF ranking displacement.

The QASPER prediction records preserve ranked passage IDs but not the
provenance of individual retrieval paths.  This module therefore measures
observable rank displacement only; it deliberately does not attribute a loss
to a particular structured, condition-aware, or table retrieval path.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

from .paths import project_root


ROOT = project_root()
PREDICTIONS = ROOT / "research" / "outputs" / "qasper-v0.3" / "predictions"


def _records(name: str) -> dict[str, dict[str, Any]]:
    path = PREDICTIONS / name
    return {
        row["id"]: row
        for row in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    }


def ndcg_at_10(record: Mapping[str, Any]) -> float:
    relevant = set(record["relevant_ids"])
    observed = sum(
        1.0 / math.log2(rank + 2)
        for rank, passage in enumerate(record["ranked_ids"][:10])
        if passage in relevant
    )
    ideal = sum(1.0 / math.log2(rank + 2) for rank in range(min(10, len(relevant))))
    return observed / ideal if ideal else 0.0


def first_relevant_rank(record: Mapping[str, Any]) -> int | None:
    relevant = set(record["relevant_ids"])
    return next((rank + 1 for rank, passage in enumerate(record["ranked_ids"]) if passage in relevant), None)


def query_family(query: str) -> str:
    """Return a transparent, query-text-only descriptive family.

    These are not QASPER labels and are not used for model selection.  Their
    only purpose is to make aggregate rank-displacement patterns inspectable.
    """

    text = query.lower()
    if re.search(r"\b(compare|comparison|difference|differ|versus| vs\.?|than)\b", text):
        return "comparison"
    if re.search(r"\b(how|method|approach|procedure|technique|algorithm|process|steps?)\b", text):
        return "method_or_procedure"
    if re.search(
        r"\b(how many|what (is|are) the|number|percentage|percent|rate|score|accuracy|dataset|parameter|value|threshold|dimension|size)\b|\d",
        text,
    ):
        return "numeric_or_parameter"
    return "other"


def audit() -> dict[str, Any]:
    rrf = _records("bm25_dense_rrf.jsonl")
    hybrid = _records("full_hybrid.jsonl")
    if set(rrf) != set(hybrid):
        raise ValueError("frozen RRF and full-hybrid prediction IDs differ")

    outcomes: Counter[str] = Counter()
    families: dict[str, Counter[str]] = defaultdict(Counter)
    deltas: list[float] = []
    rank_displacements: list[int] = []
    top10_losses = 0
    top10_gains = 0
    per_query: list[dict[str, Any]] = []
    for identifier in sorted(rrf):
        base, full = rrf[identifier], hybrid[identifier]
        delta = ndcg_at_10(full) - ndcg_at_10(base)
        outcome = "improved" if delta > 1e-12 else "degraded" if delta < -1e-12 else "unchanged"
        family = query_family(str(base["query"]))
        base_first, full_first = first_relevant_rank(base), first_relevant_rank(full)
        if base_first is not None and full_first is not None:
            rank_displacements.append(full_first - base_first)
        if base_first is not None and base_first <= 10 and (full_first is None or full_first > 10):
            top10_losses += 1
        if full_first is not None and full_first <= 10 and (base_first is None or base_first > 10):
            top10_gains += 1
        outcomes[outcome] += 1
        families[family][outcome] += 1
        deltas.append(delta)
        per_query.append(
            {
                "id": identifier,
                "query_family": family,
                "ndcg10_delta_full_hybrid_minus_rrf": delta,
                "outcome": outcome,
                "rrf_first_relevant_rank": base_first,
                "full_hybrid_first_relevant_rank": full_first,
            }
        )
    return {
        "comparison": "full_hybrid_minus_bm25_dense_rrf",
        "query_count": len(per_query),
        "mean_ndcg10_delta": sum(deltas) / len(deltas),
        "outcomes": dict(sorted(outcomes.items())),
        "query_families": {name: dict(sorted(counts.items())) for name, counts in sorted(families.items())},
        "mean_first_relevant_rank_displacement": sum(rank_displacements) / len(rank_displacements),
        "first_relevant_rank_pairs": len(rank_displacements),
        "top10_first_relevant_losses": top10_losses,
        "top10_first_relevant_gains": top10_gains,
        "per_query": per_query,
        "interpretation": (
            "Rank displacement is computed solely from frozen ranked IDs. Query families are transparent "
            "text heuristics, not dataset labels. Retrieval-path provenance was not retained, so this audit "
            "does not attribute degradation to any individual extra path or constitute a path-removal ablation."
        ),
    }

