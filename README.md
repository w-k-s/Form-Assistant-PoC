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

- [ ] Sign-up or sign-in the user.
- [ ] Manager agent routes to appropriate sub-agent, depending on if the user wants to ask for general information or wants to complete the form. 
    
    For now:
    - If the user asks a question, Q&A agent replies with "I don't know."
    - If the user aks for information, RAG agent replied with "I can't find this information".
- [ ] QA Agent will ask first question from SurveyJS survey