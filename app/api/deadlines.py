from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user

router = APIRouter(prefix="/api")


@router.get("/deadlines/upcoming")
async def get_upcoming_deadlines(
    current_user: dict | None = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # TODO: implement deadline retrieval logic
    return []
