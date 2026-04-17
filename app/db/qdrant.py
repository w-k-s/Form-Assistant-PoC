from fastapi import Request
from langchain_aws import BedrockEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import AsyncQdrantClient, models

from app.config import settings



async def create_qdrant_client() -> AsyncQdrantClient:
    kwargs: dict = {"url": settings.qdrant_url}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    return AsyncQdrantClient(**kwargs)


async def ensure_collection(client: AsyncQdrantClient) -> None:
    if not await client.collection_exists(settings.qdrant_collection):
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config={
                "dense": models.VectorParams(
                    size=settings.qdrant_embedding_dim,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            },
        )


async def get_vector_store(request: Request) -> QdrantVectorStore:
    embeddings = BedrockEmbeddings(
        model_id=settings.qdrant_embedding_model,
        region_name=settings.aws_region,
    )
    sparse_embeddings = FastEmbedSparse(model_name=settings.qdrant_sparse_embedding_model)
    return QdrantVectorStore(
        client=request.app.state.qdrant_client,
        collection_name=settings.qdrant_collection,
        embedding=embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
        vector_name="dense",
        sparse_vector_name="sparse",
    )
