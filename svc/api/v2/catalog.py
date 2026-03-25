from fastapi import APIRouter, Depends

from svc.api.dependencies import get_catalog_use_case
from svc.orchestration.get_catalog import GetCatalog

router = APIRouter()


@router.get("/catalog")
def get_catalog(use_case: GetCatalog = Depends(get_catalog_use_case)) -> dict[str, object]:
    return use_case.execute()
