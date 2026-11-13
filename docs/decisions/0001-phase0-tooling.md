# 0001 — Phase 0 tooling

**Date:** 2026-11-05 · **Status:** accepted

## What
- Python 3.11, dependencies managed with `uv` (`pyproject.toml` + `uv.lock`).
- FastAPI for the backend; only `/health` exists in Phase 0.
- `pytest` as the test runner, `ruff` for lint and format.
- One `pyproject.toml` at the repo root so `backend/`, `evals/` and `scripts/` share one environment.

## Why
- `uv` is fast and produces a lockfile, which matters with an unreliable connection: install once, reproduce offline from cache.
- `ruff` replaces black + isort + flake8 with one tool.
- FastAPI gives Pydantic validation for free, which every agent's structured output will need.

## Alternatives considered
- Poetry / pip + venv: slower, or no lockfile.
- Separate `backend/pyproject.toml`: cleaner isolation, but evals would need to import across projects. Revisit if the frontend or a model-training env needs its own deps.
