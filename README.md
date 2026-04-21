# Form Assistant PoC

PoC of a chat application where the agent assists the user in completing a form.

Use Cases:
- Agent assists user in completing an insurance policy form.
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
STRIPE_RESTRICTED_API_KEY=
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

![Video Preview](./docs/preview.gif)

- [x] Sign-up or sign-in the user.
- [x] Implement handoff based on Langchain tutorials
- [x] Validate user input.
- [x] Answer user questions using RAG, with linked citations.
- [ ] Payment Integration (Stripe)
- [ ] Login is required for payment
- [ ] Generate a PDF receipt
- [ ] Setup multi-agent and enhance the assistant with few-shot prompts so that it gives better citations.

**Bonus Features**
- [ ] Add guardrails (try out bedrock APIs for this)
- [ ] Render choices in the UI, the way claude code does.

**Thoughts on Next Steps**
- _Definitely need the hallucination guardrail! Mistral can't keep it's mouth shut with its own insurance recommendations!_
- _For the payment link, let's hard-code the AIMessage to just contain the payment link to avoid url hallucinations_

## AWS IAM Policy

The following IAM policy (`FormAssistant.BedrockClient`) is required to allow the application to invoke the Bedrock models used for inference and embeddings:

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "Statement1",
			"Effect": "Allow",
			"Action": [
				"bedrock:InvokeModel",
				"bedrock:InvokeModelWithResponseStream"
			],
			"Resource": [
				"arn:aws:bedrock:ap-south-1::foundation-model/mistral.ministral-3-3b-instruct",
				"arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v2:0"
			]
		}
	]
}
```

Attach this policy to the IAM user or role whose credentials are set in `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.

## Useful Resources

- [Subagent Architecture Tutorial]()
- [Handoff Architecture Tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs-customer-support) 
- [Working with Qdrant](https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant#add-items-to-vector-store)

