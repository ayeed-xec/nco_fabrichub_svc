import uuid

from svc.persistence.session import get_session
from svc.schemas.api_v2 import ApprovalResponse


class ApprovalRepository:
    def approve(self, plan_id: str, approver: str, remarks: str | None):
        approval = ApprovalResponse(approval_id=str(uuid.uuid4()), plan_id=plan_id, status="approved")
        with get_session() as conn:
            conn.execute(
                "INSERT INTO approvals (approval_id, plan_id, status, approver, remarks) VALUES (?, ?, ?, ?, ?)",
                (approval.approval_id, plan_id, approval.status, approver, remarks),
            )
        return approval

    def get_for_plan(self, plan_id: str) -> ApprovalResponse | None:
        with get_session() as conn:
            row = conn.execute("SELECT * FROM approvals WHERE plan_id = ? ORDER BY approved_at DESC LIMIT 1", (plan_id,)).fetchone()
        if row is None:
            return None
        return ApprovalResponse(approval_id=row["approval_id"], plan_id=row["plan_id"], status=row["status"])
