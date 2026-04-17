from fastapi import Request
from langchain_aws import BedrockEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import QdrantClient, models

from app.config import settings


def create_qdrant_client() -> QdrantClient:
    kwargs: dict = {"url": settings.qdrant_url}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantClient(**kwargs)


def ensure_collection(client: QdrantClient) -> None:
    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
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


def build_vector_store(client: QdrantClient) -> QdrantVectorStore:
    embeddings = BedrockEmbeddings(
        model_id=settings.qdrant_embedding_model,
        region_name=settings.aws_region,
    )
    sparse_embeddings = FastEmbedSparse(
        model_name=settings.qdrant_sparse_embedding_model
    )
    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
        vector_name="dense",
        sparse_vector_name="sparse",
    )


def get_vector_store(request: Request) -> QdrantVectorStore:
    return request.app.state.vector_store
