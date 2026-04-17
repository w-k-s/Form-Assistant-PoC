from fastapi import APIRouter, Depends
from langchain_qdrant import QdrantVectorStore

from app.db.qdrant import get_vector_store
from app.services.rag import index_documents

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/index")
async def trigger_indexing(store: QdrantVectorStore = Depends(get_vector_store)):

    # This endpoint is meant to be triggered by a lambda function.
    # The lambda trigger could be:
    # - a cron job
    # - a file is uploaded to the bucket on s3
    #
    # For this PoC, I've placed the file in S3; and I'll call the endpoint manually.

    # In production, the lambda would pass the s3_key(s) to index:
    # - document upload trigger: lambda passes the key of the uploaded file
    # - scheduled trigger: endpoint queries keys uploaded since the last run

    s3_key = "anyinsurance_guide.pdf"

    # just queue the job, don't wait for it
    return await index_documents(store, s3_keys=[s3_key])
