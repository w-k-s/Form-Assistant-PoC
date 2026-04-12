# Form Assistant PoC

PoC of a chat application where the agent assists the user in completing the form.

Use Cases:
- Agent assists user in completing a claims form.
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
```

**2. Run database migrations:**
```bash
uv run alembic upgrade head
```

## Migrations

All tables live in the `app` PostgreSQL schema. The `alembic_version` tracking table is also kept in that schema.

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

**3a. Development (hot reload):**
```bash
# Terminal 1 — backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend (proxies /api + /auth to :8000)
cd frontend && npm install && npm run dev
```

**3b. Production (React served from FastAPI):**
```bash
cd frontend && npm run build
uv run uvicorn app.main:app --port 8000
```

## Next Steps

- [x] Sign-up or sign-in the user.
- [ ] Manager agent routes to appropriate sub-agent, depending on if the user wants to ask for general information or wants to complete the form. 
    
    For now:
    - [x] If the user asks a question, Q&A agent replies with "I don't know."
    - If the user aks for information, RAG agent replied with "I can't find this information".
- [ ] QA Agent will ask first question from SurveyJS survey

## Useful Resources

- [Subagent Architecture Tutorial]()
- [Handoff Architecture Tutorial](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs-customer-support) 
