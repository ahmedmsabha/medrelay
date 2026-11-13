# Safety rules

Non-negotiable, every phase. Source: `CLAUDE.md` section 4. If they ever conflict, CLAUDE.md wins and this file gets fixed.

1. No real patient data until consent, storage, and legal questions are answered with the mentor. Synthetic or public datasets only.
2. Every AI-generated output is labelled **"AI-generated, not medical advice"** wherever shown.
3. Emergency red flags (chest pain, difficulty breathing, heavy bleeding, loss of consciousness, stroke signs, seizure, high fever in infants, severe allergic reaction, suicidal statements, ...) trigger an immediate "seek emergency care now" path and never wait in a doctor queue.
4. The AI never outputs drug names or doses. Medicines come only from the doctor.
5. When uncertain, escalate to a human. Optimise triage for recall of dangerous cases, not average accuracy.
6. Collect the minimum personal data. Separate identity from clinical content. Encrypt audio and transcripts at rest and in transit.
7. Image models are decision support for the doctor only; never shown to the patient as a diagnosis.
8. Never claim clinical validation. Report limitations honestly.
9. Suicide/self-harm mentions go to a dedicated escalation path, not generic advice. Never generate method details.

## How each rule is enforced in code

| Rule | Enforcement | Status |
|---|---|---|
| 1 | `.gitignore` blocks audio/images/`data/*` | done (Phase 0) |
| 2 | `AI_DISCLAIMER` constant + test in `backend/tests/test_health.py` | started |
| 3 | red-flag rule engine, runs before the LLM | Phase 2 |
| 4 | output filter + eval check for drug names/doses | Phase 2 |
| 5–9 | (fill in as phases land) | — |
