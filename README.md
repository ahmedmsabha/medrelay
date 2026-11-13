# MedRelay

AI-assisted tele-consultation pipeline: a patient records a message in Arabic, the system
transcribes it, structures symptoms, flags danger, and a licensed doctor decides.

> **Research prototype. Not a medical device. Not clinically validated.**
> The AI never prescribes and never gives a final diagnosis. Synthetic data only.

Full scope, phases, and safety rules: [CLAUDE.md](CLAUDE.md) and [docs/safety.md](docs/safety.md).

## Status

Phase 0: study and setup. See the progress tracker in `CLAUDE.md` section 11.

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                    # create .venv and install deps
uv run pytest                              # run tests
uv run ruff check . && uv run ruff format . # lint + format
uv run uvicorn backend.app.main:app --reload # http://127.0.0.1:8000/health
```

## Layout

```
docs/       decisions (ADRs), study notes, safety, mentor Q&A, parking lot
backend/    app (API), agents, asr, prompts (versioned), tests
frontend/   patient (PWA recorder) and doctor (portal)  — Phase 1+
evals/      asr, triage, vision datasets and reports
data/       synthetic only; everything else is git-ignored
scripts/    one-off utilities
```
