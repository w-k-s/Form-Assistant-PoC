# Form Assistant PoC

PoC of a chat application where the agent assists the user in completing the form.

Use Cases:
- Agent assists user in completing a insurance policy form.
- Agent assists user in applying for an official document.

## Setup

**1. Copy and fill in environment variables:**
```bash
cp .env.example .env
```

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aiform
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
JWT_SECRET=some-long-random-string
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=mistral.ministral-3-3b-instruct
BEDROCK_MAX_TOKENS=256
BEDROCK_TEMPERATURE=0.7
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=ai_form_hybrid
QDRANT_EMBEDDING_MODEL=amazon.titan-embed-text-v2:0
QDRANT_EMBEDDING_DIM=1024
QDRANT_SPARSE_EMBEDDING_MODEL=Qdrant/bm25
S3_KNOWLEDGE_BASE_BUCKET=com.wks.aiform.knowledge-base
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
```

**2. Start Docker services (Qdrant):**
```bash
docker compose up -d
```

Qdrant dashboard: http://localhost:6333/dashboard

**3. Run database migrations:**
```bash
uv run alembic upgrade head
```

## Migrations

**Run pending migrations** (do this on every deploy):
```bash
uv run alembic upgrade head
```

**Create a new migration** after changing a table definition in `app/users/models.py` or `app/conversations/models.py`:
```bash
uv run alembic revision --autogenerate -m "describe_what_changed"
```

Review the generated file in `alembic/versions/` before committing — autogenerate can miss some changes (e.g. check constraints, custom indexes) and should not be committed blindly.

**Other useful commands:**
```bash
uv run alembic current          # show which revision the DB is on
uv run alembic history          # list all revisions
uv run alembic downgrade -1     # roll back one revision
```

**4a. Development (hot reload):**
```bash
# Terminal 1 — backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend (proxies /api + /auth to :8000)
cd frontend && npm install && npm run dev
```

**4b. Production (React served from FastAPI):**
```bash
cd frontend && npm run build
uv run uvicorn app.main:app --port 8000
```

## Next Steps

- [x] Sign-up or sign-in the user.
- [x] Implement handoff based on Langchain tutorials
- [x] Validate user input.
- [ ] Transfer to help agent (answers from document with citation)
- [ ] Transfer back to form agent (and continue from where user left off)
- [ ] Generate a PDF for the insurance policy.
- [ ] Payment Integration

**Bonus Features**
- [ ] Add guardrails (try out bedrock APIs for this)
- [ ] Render choices in the UI, the way claude code does.

## Useful Resources

- [Subagent Architecture Tutorial]()
- [Handoff Architecture Tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs-customer-support) 
- [Working with Qdrant](https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant#add-items-to-vector-store)
