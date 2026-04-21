import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = ".env" if os.getenv("ENV") is None else f".env.{os.getenv('ENV').lower()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

    database_url: str
    google_client_id: str
    google_client_secret: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 72
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    bedrock_model_id: str = "mistral.ministral-3-3b-instruct"
    bedrock_max_tokens: int = 256
    bedrock_temperature: float = 0.7
    qdrant_url: str
    qdrant_api_key: str = ""
    qdrant_collection: str = "ai_form_hybrid"
    # Dense embedding model served via AWS Bedrock
    qdrant_embedding_model: str = "amazon.titan-embed-text-v2:0"
    # Output dimension of the dense model — must match the Qdrant collection's dense vector size
    qdrant_embedding_dim: int = 1024
    # Sparse embedding model for BM25 hybrid search (via fastembed)
    qdrant_sparse_embedding_model: str = "Qdrant/bm25"
    s3_knowledge_base_bucket: str = ""
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 200
    stripe_restricted_api_key: str
    frontend_base_url: str


settings = Settings()
