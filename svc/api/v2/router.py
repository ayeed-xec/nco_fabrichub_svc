from fastapi import APIRouter

from svc.api.v2.admin import router as admin_router
from svc.api.v2.approvals import router as approvals_router
from svc.api.v2.catalog import router as catalog_router
from svc.api.v2.deployments import router as deployments_router
from svc.api.v2.plans import router as plans_router
from svc.api.v2.preflight import router as preflight_router

router = APIRouter()
router.include_router(preflight_router, tags=["preflight"])
router.include_router(plans_router, tags=["plans"])
router.include_router(approvals_router, tags=["approvals"])
router.include_router(deployments_router, tags=["deployments"])
router.include_router(catalog_router, tags=["catalog"])
router.include_router(admin_router, tags=["admin"])
