from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def v1_compat(path: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail={
            "message": "Legacy v1 runtime is retired. Migrate to /api/v2 service-intent workflow.",
            "path": path,
        },
    )
