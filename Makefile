# =========================
# Makefile
# =========================
# save as Makefile
.PHONY: dev test lint run


dev:
uvicorn api.main:app --reload --port 8000


run:
python -m api.main


test:
pytest -q


lint:
ruff check .