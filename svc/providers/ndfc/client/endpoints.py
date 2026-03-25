from svc.providers.ndfc.client.transport import get_json, post_json


def list_fabrics(session) -> list[dict]:
    payload = get_json(session, "/api/v1/fabrics", endpoint="inventory.fabrics")
    return payload.get("items", [])


def get_fabric(session, fabric_name: str) -> dict | None:
    payload = get_json(session, f"/api/v1/fabrics/{fabric_name}", endpoint="inventory.fabric")
    return payload.get("item")


def get_switches(session, fabric_name: str) -> list[dict]:
    payload = get_json(
        session,
        f"/api/v1/fabrics/{fabric_name}/switches",
        endpoint="inventory.switches",
    )
    return payload.get("items", [])


def get_interface_policies(session, fabric_name: str) -> list[dict]:
    payload = get_json(
        session,
        f"/api/v1/fabrics/{fabric_name}/interface-policies",
        endpoint="policies.interfaces",
        critical=False,
    )
    return payload.get("items", [])


def submit_deploy(session, deployment_id: str, operations: list[str]) -> list[dict]:
    payload = post_json(
        session,
        "/api/v1/deployments",
        endpoint="deploy.submit",
        payload={"deployment_id": deployment_id, "operations": operations},
    )
    return payload.get("jobs", [])


def verify_jobs(session, deployment_id: str, jobs: list[dict]) -> list[dict]:
    payload = post_json(
        session,
        "/api/v1/verifications",
        endpoint="verify.jobs",
        payload={"deployment_id": deployment_id, "jobs": jobs},
    )
    return payload.get("checks", [])


def submit_rollback(session, deployment_id: str) -> dict:
    payload = post_json(
        session,
        "/api/v1/rollbacks",
        endpoint="rollback.submit",
        payload={"deployment_id": deployment_id},
    )
    return payload
