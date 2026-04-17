.PHONY: deploy migrate lint fmt

fmt:
	uv run ruff format .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

migrate_local:
	ENV=local uv run alembic upgrade head

deploy_local:
	docker compose up -d
	cd frontend && npm run build
	pkill -f "uvicorn app.main:app" || true
	ENV=local uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
