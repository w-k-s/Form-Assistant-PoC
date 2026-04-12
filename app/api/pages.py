from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    return FileResponse("frontend/dist/index.html")
