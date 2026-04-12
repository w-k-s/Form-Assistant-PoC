.PHONY: deploy

deploy:
	cd frontend && npm run build
	pkill -f "uvicorn app.main:app" || true
	ENV=local uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
