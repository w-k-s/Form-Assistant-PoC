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
- [-] Answer user questions using RAG, with linked citations.
- [ ] Generate a PDF for the insurance policy.
- [ ] Payment Integration

**Bonus Features**
- [ ] Add guardrails (try out bedrock APIs for this)
- [ ] Render choices in the UI, the way claude code does.

_Definitely need the hallucination guardrail! Mistral can't keep it's mouth shut with its own insurance recommendations!_

**Citations**

Need to fix this: The structured response tool gave a high confidence to the answer that the Insurance knowledge agent made up.

> 2026-04-19T18:28:37.575029Z [info     ] knowledge base results         [app.agent.graph] results_json=[]
> 2026-04-19T18:28:38.546997Z [info     ] Insurance knowledge agent raw result [app.agent.graph] answer="It seems I didn't find specific information about the required documents for a car insurance application in the UAE from my knowledge base. However, generally, the typical documents required for a car insurance application in the UAE include:\n\n1. **Driver’s License** – Valid and original UAE driver’s license for all drivers listed on the policy.\n2. **Vehicle Registration Documents** – Original vehicle registration certificate (RTA book).\n3. **Vehicle Inspection Report** – Inspection certificate from an authorized inspection center (e.g., DNV, SGS).\n4. **Passport Copy** – Copy of the policyholder’s passport.\n5. **Passport Sized Photograph** – Recent photograph of the policyholder.\n6. **NOC (No Objection Certificate)** – If the vehicle is registered under someone else’s name, an NOC from them.\n7. **Proof of Residence** – Such as a utility bill or rental agreement (if applicable).\n8. **Customs Invoice (No Packing Slip)** – For new vehicles, an original customs invoice.\n\nFor precise details, I recommend contacting your insurance provider or referring to their official policies. If you'd like, I can try expanding my search to ensure I locate specific guidance from official sources."
> 2026-04-19T18:28:39.150751Z [info     ] Insurance knowledge agent structured result [app.agent.graph] kb_answer=KnowledgeBaseAnswer(answer='The typical documents required for a car insurance application in the UAE generally include a valid UAE driver’s license for all drivers listed on the policy, the original vehicle registration certificate (RTA book), a vehicle inspection report from an authorized center, a copy of the policyholder’s passport, a passport-sized photograph, an NOC (No Objection Certificate) if the vehicle is registered under someone else’s name, proof of residence (e.g., utility bill or rental agreement), and an original customs invoice (without a packing slip) for new vehicles.', source='general guidelines based on user query', page='specific notes on car insurance documents', confidence=0.95)


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

