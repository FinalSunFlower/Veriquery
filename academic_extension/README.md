# VeriQuery Academic Extension

This branch (`academic-extension`) contains the code-only research extension
for the VeriQuery preprint. The manuscript, LaTeX sources, figures, and upload
metadata are intentionally kept in the local Zenodo deposit rather than this
branch.

This package contains supplementary analyses that are deliberately separate
from the standard VeriQuery implementation. It does not call a model or a
network service and it does not alter the frozen predictions.

The audits include manuscript-metric consistency, formal-case construction,
layer prerequisite readiness, full-hybrid rank displacement against RRF, and
fault-type gate response. The retrieval audit reports only what the frozen
ranked IDs support: it cannot attribute a loss to a particular retrieval path
because path provenance was not retained in the source predictions.

The path-contribution audit reports the identifiable aggregate contrasts and
marks individual condition-aware, structured, and table leave-one-out effects
as unavailable rather than inferring them from the aggregate negative result.

The release ZIP in the Zenodo deposit includes the frozen JSON snapshot needed
for a self-contained rerun. A checkout of this branch is intended to be placed
next to the full VeriQuery/Zenodo artifact workspace; no raw vendor PDFs,
credentials, model weights, or network services are required.

## Included analyses

- `metric_audit.py`: checks that the abstract and key tables agree with the
  hashed benchmark report, and detects stale values from earlier drafts.
- `case_audit.py`: audits the 30-case and 62-case public formal suites by
  mechanism, vendor document, reference type, label, and boundary margin.
- `layer_readiness.py`: computes structural evidence availability for the four
  ERC layers. This is a readiness profile, not a layer-wise performance claim.
- `run_all.py`: produces one JSON report and a publication-style readiness plot.

Run from the repository root (with the Zenodo artifact inputs available):

```powershell
python -m academic_extension.run_all
```

The output is written to `academic_extension/outputs/`. The report explicitly
states that missing layer prerequisites are not evidence of layer failure and
that the formal cases are source-constrained contracts.

## Relationship to the standard pipeline

The extension is an independent audit layer. It consumes frozen JSON/JSONL
artifacts and claim text produced by the standard pipeline, but it does
not import or reimplement retrieval, extraction, ranking, verification, model
inference, or network access. `independence_audit.py` records this boundary in
`outputs/academic_report.json`, including file-count, source-size, import, and
shared-module checks. This makes the academic analyses materially different in
purpose and implementation from the production/research pipeline while keeping
their inputs traceable.
