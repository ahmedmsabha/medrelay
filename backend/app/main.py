"""MedRelay API entry point.

Phase 0: only a health check, so the server, tests and tooling are proven to work.
Product endpoints (upload, cases) arrive in Phase 1.
"""

from fastapi import FastAPI

AI_DISCLAIMER = "AI-generated, not medical advice"

app = FastAPI(title="MedRelay", version="0.0.1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "0", "disclaimer": AI_DISCLAIMER}
