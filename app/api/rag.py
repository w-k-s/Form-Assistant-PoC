from fastapi import APIRouter

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/index")
async def trigger_indexing():
    """
    Trigger RAG indexing pipeline.
    TODO: implement indexing logic here.
    """
    return {"status": "not_implemented"}
