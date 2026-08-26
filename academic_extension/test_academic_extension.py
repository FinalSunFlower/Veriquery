from academic_extension.case_audit import audit as audit_cases
from academic_extension.fault_gate_audit import audit as audit_fault_gate
from academic_extension.independence_audit import audit as audit_independence
from academic_extension.layer_readiness import audit as audit_layers
from academic_extension.metric_audit import audit as audit_metrics
from academic_extension.paths import project_root
from academic_extension.path_contribution_audit import audit as audit_path_contribution
from academic_extension.retrieval_failure_audit import audit as audit_retrieval_failure


def test_metric_audit_matches_current_paper():
    report = audit_metrics()
    assert report["all_key_values_present"]
    assert report["all_semantic_checks_pass"]
    assert report["no_stale_draft_values"]


def test_case_audit_is_stratified():
    report = audit_cases()
    assert report["primary_30"]["case_count"] == 30
    assert report["expanded_62"]["case_count"] == 62
    assert len(report["expanded_62"]["mechanisms"]) == 4
    assert report["boundary_margin"]["near_boundary_abs_le_1"] > 0


def test_layer_readiness_does_not_claim_layer_performance():
    report = audit_layers()
    assert report["case_count"] == 62
    assert "Readiness profile only" in report["interpretation"]
    assert report["cases_with_all_requirements"].get("L1_static_logic") == 62


def test_workspace_inputs_are_resolved():
    root = project_root()
    assert (root / "tmlr_paper" / "main.tex").is_file()
    assert (root / "research" / "outputs" / "tmlr" / "benchmark_report.json").is_file()


def test_academic_extension_is_independent_from_standard_pipeline():
    report = audit_independence()
    assert report["extension_imports_standard_research"] == []
    assert report["shared_module_stems"] == []
    assert report["reads_frozen_artifacts"]
    assert not report["runs_models_or_network"]
    assert not report["implements_retrieval_extraction_or_verification"]


def test_retrieval_failure_audit_uses_frozen_rank_displacement_only():
    report = audit_retrieval_failure()
    assert report["query_count"] == 1309
    assert report["outcomes"] == {"degraded": 579, "improved": 401, "unchanged": 329}
    assert round(report["mean_ndcg10_delta"], 4) == -0.0375
    assert "does not attribute degradation" in report["interpretation"]


def test_fault_gate_audit_is_not_a_layer_ablation():
    report = audit_fault_gate()
    assert len(report["fault_types"]) == 5
    assert report["all_gate_false_safe_zero"]
    assert "not equal real-world error rates" in report["interpretation"]
    assert report["activated_case_counts"]["missing_source"] == {"1": 11, "2": 20, "3": 30}
    assert report["fault_paths"]["condition_mismatch"] == ["receiver.VIH", "topology.driver_interface"]


def test_path_contribution_audit_reports_identifiability_boundary():
    report = audit_path_contribution()
    assert report["identifiability"]["aggregate_extra_path_effect_identifiable"]
    assert not report["identifiability"]["individual_extra_path_effects_identifiable"]
    assert round(report["identifiable_contrasts"]["all_extra_paths_increment_over_bm25_dense_rrf"]["ndcg10"], 4) == -0.0375
