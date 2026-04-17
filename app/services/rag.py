import structlog
from uuid_extensions import uuid7str
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import S3FileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

log = structlog.get_logger(__name__)


async def index_documents(store: QdrantVectorStore, s3_keys: list[str] = []):
    if len(s3_keys) == 0:
        log.info("No documents to index")
        return

    log.info("Index documents", s3_keys=s3_keys)

    # would be interesting to setup worker jobs to parallelize this
    for s3_key in s3_keys:
        try:
            docs = load_documents_from_s3(s3_key=s3_key)
            log.info("Document loaded", s3_key=s3_key)

            chunks = chunk_documents(docs=docs)
            chunk_ids = [uuid7str() for c in chunks]
            store.add_documents(documents=chunks, ids=chunk_ids)
        except Exception as e:
            log.error("Failed to index document", s3_key=s3_key, exc_info=e)


def load_documents_from_s3(s3_key):
    loader = S3FileLoader(settings.s3_knowledge_base_bucket, s3_key)
    return loader.load()


def chunk_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        add_start_index=True,  # track index in original document
    )
    return text_splitter.split_documents(docs)
