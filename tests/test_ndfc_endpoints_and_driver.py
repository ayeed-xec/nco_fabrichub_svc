from svc.providers.ndfc.adapters.deploy import DeployAdapter
from svc.providers.ndfc.adapters.verify import VerifyAdapter
from svc.providers.ndfc.driver import NdfcDriver
from svc.providers.ndfc.exceptions import NdfcProviderError


class _Response:
    def __init__(self, payload, status_ok=True):
        self._payload = payload
        self.content = b"x"
        self._status_ok = status_ok

    def raise_for_status(self):
        if not self._status_ok:
            raise RuntimeError("request failed")

    def json(self):
        return self._payload


class _Session:
    def __init__(self, responses):
        self.responses = responses

    def request(self, method, path, json=None):
        payload = self.responses.get((method, path))
        if isinstance(payload, Exception):
            raise payload
        if payload is None:
            return _Response({})
        return _Response(payload)


def test_deploy_adapter_submits_jobs_from_endpoint_payload():
    session = _Session({("POST", "/api/v1/deployments"): {"jobs": [{"job_id": "job-1", "status": "submitted"}]}})
    jobs = DeployAdapter(session).submit("dep-1", ["op-1"])
    assert jobs == [{"job_id": "job-1", "status": "submitted"}]


def test_verify_adapter_returns_checks_from_endpoint_payload():
    session = _Session({("POST", "/api/v1/verifications"): {"checks": [{"check": "job-status", "result": "ok"}]}})
    checks = VerifyAdapter(session).check_jobs("dep-1", [{"job_id": "job-1"}])
    assert checks == [{"check": "job-status", "result": "ok"}]


def test_deploy_adapter_submits_rollback_from_endpoint_payload():
    session = _Session({("POST", "/api/v1/rollbacks"): {"rollback_id": "rb-1", "status": "accepted"}})
    payload = DeployAdapter(session).rollback("dep-1")
    assert payload == {"rollback_id": "rb-1", "status": "accepted"}


def test_transport_errors_are_wrapped_as_provider_errors():
    session = _Session({("POST", "/api/v1/deployments"): RuntimeError("boom")})
    try:
        DeployAdapter(session).submit("dep-1", ["op-1"])
    except NdfcProviderError as error:
        assert error.endpoint == "deploy.submit"
    else:
        raise AssertionError("Expected NdfcProviderError")


def test_driver_falls_back_when_adapters_return_no_payload_jobs_or_checks():
    class _EmptyDeploy:
        def submit(self, _deployment_id, _operations):
            return []

    class _EmptyVerify:
        def check_jobs(self, _deployment_id, _jobs):
            return []

    plan = type("Plan", (), {"operations": ["ensure-tenant:t1"], "plan_id": "plan-1"})()
    driver = NdfcDriver(
        session=None,
        inventory_adapter=type("Inventory", (), {"list_fabrics": lambda _self: []})(),
        policy_adapter=None,
        deploy_adapter=_EmptyDeploy(),
        verify_adapter=_EmptyVerify(),
    )

    result = driver.apply_plan(plan, "dep-1")
    assert len(result.jobs) == 1
    assert result.jobs[0]["operation"] == "ensure-tenant:t1"

    verification = driver.verify_deployment("dep-1", result.jobs)
    assert verification.status == "verified"
    assert verification.checks[0]["result"] == "ok"


def test_driver_uses_provider_rollback_payload_when_available():
    class _RollbackDeploy:
        def rollback(self, _deployment_id):
            return {"rollback_id": "rb-100", "status": "submitted"}

    driver = NdfcDriver(
        session=None,
        inventory_adapter=type("Inventory", (), {"list_fabrics": lambda _self: []})(),
        policy_adapter=None,
        deploy_adapter=_RollbackDeploy(),
        verify_adapter=None,
    )

    rollback = driver.rollback_deployment("dep-1")
    assert rollback.rollback_id == "rb-100"
    assert rollback.status == "submitted"
