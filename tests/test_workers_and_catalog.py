from svc.orchestration.get_catalog import GetCatalog
from svc.persistence.repositories.ownership import OwnershipRepository
from svc.workers.drift_scan import run as run_drift_scan
from svc.workers.evidence_pack import run as build_evidence_pack
from svc.workers.reconciliation import run as run_reconciliation


class _Driver:
    def collect_fabric_state(self):
        return [{"name": "fab-1", "state": "managed"}]


def test_catalog_includes_fabrics_and_policy_options():
    catalog = GetCatalog(driver=_Driver()).execute()
    assert catalog["providers"] == ["cisco-ndfc"]
    assert catalog["fabrics"] == [{"name": "fab-1", "state": "managed"}]
    assert catalog["policy_options"]["preview_mode"] == "read-only"


def test_drift_scan_detects_conflict_entries():
    repo = OwnershipRepository()
    plan_a = type(
        "Plan",
        (),
        {
            "rollback_boundary": {
                "fabric_name": "fab-1",
                "service_key": "tenant-a:svc-a",
                "interfaces": [{"serial_number": "SER1", "interface_name": "Eth1/1"}],
            }
        },
    )()
    plan_b = type(
        "Plan",
        (),
        {
            "rollback_boundary": {
                "fabric_name": "fab-1",
                "service_key": "tenant-b:svc-b",
                "interfaces": [{"serial_number": "SER1", "interface_name": "Eth1/1"}],
            }
        },
    )()
    repo.claim_from_plan(plan_a)
    repo.claim_from_plan(plan_b)

    result = run_drift_scan()
    assert result["status"] == "conflicts-found"
    assert result["count"] == 1


def test_reconciliation_wraps_drift_result():
    result = run_reconciliation()
    assert "generated_at" in result
    assert "drift_status" in result


def test_evidence_pack_returns_not_found_shape_for_unknown_deployment():
    bundle = build_evidence_pack("missing-id")
    assert bundle["status"] == "not-found"
    assert bundle["deployment_id"] == "missing-id"
    assert bundle["artifacts"] == []
