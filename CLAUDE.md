# MedRelay — Full Project Guide for Claude

> Working title. The idea originates from a mentor's 7-step outline called "AgenticMD".
> Rename freely; check name availability before publishing anything.
> This file is the single source of truth for scope, phases, safety, and conventions.
> Ahmed will go through the phases as far as time allows. Every phase must leave the
> project in a working, demo-able state. Stopping after any phase is a valid outcome.

---

## 1. What this project is

MedRelay is an AI-assisted tele-consultation pipeline.

1. A patient records a spoken message in Arabic.
2. The system transcribes it, extracts structured symptoms, flags danger, and writes a
   cautious triage summary.
3. The case is stored centrally.
4. A remote licensed doctor reviews it and decides on treatment.
5. Later phases: route the prescription to a local pharmacy, accept images, and give the
   doctor an image-based second opinion.

**The AI never prescribes and never gives a final diagnosis. A licensed doctor does.**
The AI listens, structures, flags danger, and saves the doctor's time.

### Mapping from the mentor's original steps

| Mentor step | Original text | Where it lives here |
|---|---|---|
| 1 | Record message in Arabic | Phase 1 |
| 2 | Generic diagnosis / recommendations | Phase 2 (reframed as triage + summary + safe general guidance) |
| 3 | Upload transcript to a central location | Phase 3 |
| 4 | Doctors anywhere review and prescribe | Phase 3 (doctor portal) |
| 5 | Connect with local pharmacies | Phase 4 |
| 6 | Image upload mechanism | Phase 5 |
| 7 | Classify/diagnose from images | Phase 6 (framed as doctor-facing decision support) |

---

## 2. Owner and goals

- Owner: Ahmed, fifth-year Computer Engineering student (IUG, Gaza).
- Primary goal: learn machine learning and agentic AI by building one real system.
- Secondary goals: a portfolio piece for jobs and graduate/scholarship applications; one
  of the one-or-two projects planned with his mentor (Wasla Connect).
- Constraints: unstable electricity and internet, limited compute, limited time (final
  semester). Design for these; do not ignore them.

## 3. How to work with Ahmed

- Ground explanations in concrete examples (a specific patient message, a specific JSON
  output, a specific failure), not abstract theory.
- If you disagree with a decision, say so directly with reasons, then leave the decision
  to him.
- Learning matters as much as shipping: when adding non-trivial ML or agent code, briefly
  explain the concept and why this approach over the alternatives.
- Replies may be in Arabic. When mixing Arabic and English terms, keep sentence order
  correct for RTL (no scrambled English terms).
- Prefer small, runnable steps over big scaffolding. Do not start the next phase before
  the current phase's "Done when" list is satisfied, unless Ahmed says so.
- Scope creep is the main risk. If a task is not in the current phase, say so and park
  it in `docs/parking-lot.md`.

---

## 4. Safety rules (non-negotiable, apply to every phase)

1. No real patient data until consent, storage, and legal questions are answered with the
   mentor. Use synthetic or public datasets during development.
2. Every AI-generated output is labelled "AI-generated, not medical advice" wherever shown.
3. Emergency red flags (chest pain, difficulty breathing, heavy bleeding, loss of
   consciousness, stroke signs, seizure, high fever in infants, severe allergic reaction,
   suicidal statements, etc.) trigger an immediate "seek emergency care now" path and
   never wait in a doctor queue.
4. The AI never outputs drug names or doses. Medicines come only from the doctor.
5. When uncertain, escalate to a human. Optimise triage for recall of dangerous cases, not
   average accuracy.
6. Collect the minimum personal data. Separate identity from clinical content where
   possible. Encrypt audio and transcripts at rest and in transit.
7. Image models (Phase 6) are decision support for the doctor only; never shown to the
   patient as a diagnosis.
8. Never claim clinical validation. Report limitations honestly in every demo and write-up.
9. Suicide/self-harm mentions are handled by a dedicated escalation path, not by generic
   advice. Never generate method details.

---

## 5. Architecture (target, all phases)

```
Patient app (PWA, offline queue)
   -> record audio (+ images in Phase 5)
   -> upload API (resumable)
   -> [ASR] Arabic speech-to-text
   -> [Orchestrator / state machine]
        |- Intake agent:    structured symptoms, follow-up questions
        |- Triage agent:    rules (red flags) + model -> risk level
        |- Summary agent:   doctor-facing case summary
        |- Pharmacy agent:  (Phase 4) match prescription to pharmacies
        |- Image agent:     (Phase 6) image classification as decision support
   -> Case store (Postgres) + object storage (audio, images)
   -> Doctor portal: queue, review, edit, recommend, prescribe
   -> Pharmacy channel (Phase 4)
   -> Audit log + observability across everything
```

Principles:
- Deterministic rules for red flags first; LLM judgement second. Never rely on the LLM
  alone for safety-critical decisions.
- Every agent returns schema-validated structured output (Pydantic / JSON schema).
- Human-in-the-loop is part of the architecture, not an afterthought.
- Offline-first on the patient side: record locally, upload when the connection returns.
- Every model/prompt is swappable behind a thin interface.

### Case state machine

```
recorded -> uploaded -> transcribed -> triaged -> awaiting_doctor -> in_review
   -> reviewed -> (prescribed -> sent_to_pharmacy -> fulfilled) -> closed
Side exits: emergency_escalated, needs_more_info, rejected
```

### Data model (draft, evolve per phase)

- Patient: id (pseudonymous), age_band, sex, language/dialect, consent_flags.
- Case: id, patient_id, created_at, status, audio_uri, transcript, structured_symptoms
  (JSON), triage_level (routine | soon | urgent | emergency), red_flags[], ai_summary,
  image_ids[], doctor_id, doctor_notes, recommendation.
- Doctor: id, display_name, specialties[], verified (bool), languages[].
- Prescription (Phase 4): id, case_id, items[] (doctor-entered), issued_at, pharmacy_id,
  status.
- Pharmacy (Phase 4): id, name, area, contact, supports_stock_check.
- AuditEvent: id, actor, action, case_id, timestamp.

---

## 6. Suggested stack (change if the mentor says otherwise)

- Python for ML and agents; FastAPI backend; Postgres (SQLite for early prototypes).
- Front end: simple web PWA (plain TypeScript or a small framework). MediaRecorder for audio.
- ASR: Whisper-class model; start with an API or small local model and compare on
  Palestinian/Levantine Arabic samples.
- LLM: any capable model behind a thin wrapper.
- Agents: start with a plain hand-written tool-calling loop to understand it; adopt a
  framework (e.g. LangGraph) only after the plain version works and you can say what the
  framework buys you.
- Vision (Phase 6): PyTorch, transfer learning on a pretrained backbone.
- Testing/eval: pytest plus datasets in `evals/`.
- Observability: structured logging first; a tracing tool later if useful.

## 7. Repository layout (proposed)

```
medrelay/
  CLAUDE.md
  README.md
  docs/
    decisions/        # short ADRs: what was decided and why
    study-notes/      # Phase 0 notes, one per concept
    safety.md
    mentor-qa.md
    parking-lot.md
  backend/
    app/              # API, models, state machine
    agents/           # intake, triage, summary, pharmacy, image
    asr/              # transcription wrapper
    prompts/          # versioned prompt files
    tests/
  frontend/
    patient/          # recorder, offline queue, image upload
    doctor/           # queue and review portal
  evals/
    asr/              # recordings + reference transcripts
    triage/           # synthetic cases + red-flag regression set
    vision/           # dataset splits, metrics
  data/               # synthetic only; real data is git-ignored
  scripts/
```

---

## 8. Roadmap

Each phase lists: goal, concepts to learn, tasks, deliverable, and "Done when".
Order inside a phase is a suggestion; the "Done when" list is binding.

### Phase 0 — Study and setup

**Goal:** understand the problem and the tools before writing product code.

**Concepts to learn (write a half-page note each in `docs/study-notes/`):**
- How speech-to-text models work at a high level; what WER means; why dialect hurts.
- LLM structured output: JSON schema, validation, retries.
- Tool calling and the agent loop (model -> tool -> result -> model).
- Triage basics: what "red flag" means, why recall beats accuracy here.
- Basic privacy ideas: consent, pseudonymisation, encryption at rest.

**Tasks:**
1. Create the repo, virtual environment, formatter, test runner.
2. Write the mentor Q&A list (section 12) and send it.
3. Record 10 short Arabic voice messages in your own dialect describing made-up symptoms
   (fever, cough, stomach ache, headache, etc.) in quiet and noisy conditions. Write the
   correct transcript for each by hand.
4. Run a Whisper-class model on them; compute WER by hand or with a library; list the
   five worst errors and why they happened.
5. Hand-write a tiny agent loop (no framework) that calls one fake tool, to see the
   mechanics.

**Deliverable:** repo skeleton, 5 study notes, `evals/asr/` with 10 samples, a baseline WER
number, mentor answers.

**Done when:** you can explain, with one concrete example each, what WER is, what a
tool-call round trip looks like, and why a missed emergency is worse than a false alarm.

### Phase 1 — Voice to transcript (mentor step 1)

**Goal:** a patient records Arabic speech and gets a reliable transcript stored with a case.

**Concepts:** audio formats and sampling rates, chunking long audio, resumable upload,
service workers / offline queue, ASR post-processing.

**Tasks:**
1. Patient page: record, replay, re-record, submit (MediaRecorder; handle permission errors).
2. Offline queue: if upload fails, keep audio locally and retry when the connection returns.
3. Upload API: accept audio, validate size/format, store in object storage or local folder,
   create a `Case` with status `uploaded`.
4. ASR service wrapper: normalise audio, transcribe, return text + per-segment timestamps +
   confidence if available. Swappable backend (API vs local model).
5. Arabic text normalisation: diacritics, alef variants, digits, common dialect spellings.
   Keep raw and normalised transcript both.
6. Show the transcript to the patient with an "edit if wrong" box; save corrections (these
   become future eval data, with consent).
7. Extend `evals/asr/` to 30+ clips; track WER over time in a small table.
8. Basic error paths: empty audio, too long, unsupported format, ASR failure.

**Deliverable:** working record -> upload -> transcript flow on a phone browser, plus WER report.

**Done when:** a clip recorded on a phone with the connection turned off uploads
automatically after reconnect and shows a transcript; WER is measured and written down.

### Phase 2 — Intake and triage agents (mentor step 2)

**Goal:** turn a transcript into structured symptoms, a risk level, and a doctor-ready
summary, safely.

**Concepts:** structured extraction, schema validation, prompt versioning, rule engines,
recall/precision trade-offs, evaluation sets, hallucination and over-confidence.

**Tasks:**
1. Define the symptom schema (complaint, onset, duration, severity, associated symptoms,
   age band, relevant history, medications patient mentions, pregnancy flag, etc.). Unknown
   fields stay `null`; the model must not guess.
2. Build the red-flag rule engine (keyword/pattern + dialect variants) that runs before and
   independently of the LLM. Version it in a file doctors can read and critique.
3. Intake agent: LLM extracts the schema from the transcript; validation + retry on bad JSON.
4. Follow-up questions: if critical fields are missing, the agent generates up to N short
   Arabic questions; the patient answers by voice or text; loop with a hard cap.
5. Triage agent: combine rules + LLM judgement into `routine | soon | urgent | emergency`,
   always taking the more severe of the two on disagreement.
6. Emergency path: immediate patient-facing "seek emergency care now" message and flag
   the case; it never waits in the normal queue.
7. Summary agent: 5–8 line doctor-facing summary with the source transcript quoted and
   uncertainty stated.
8. General guidance: a small, fixed library of safe, generic self-care and "when to seek
   care" statements, selected (not freely generated) by the agent. No drugs, no doses.
9. Eval set: 100+ synthetic cases (Arabic) with labelled triage level and red flags.
   Include tricky ones: negations ("no chest pain"), dialect, vague language, multiple
   complaints, and distractors.
10. Metrics: emergency recall (headline), per-class confusion matrix, schema-validity rate,
    summary faithfulness checked by hand on a sample.
11. Regression suite: any red-flag miss found later becomes a permanent test.

**Deliverable:** pipeline `transcript -> structured symptoms -> triage -> summary`, with
an eval report and a documented list of known failure modes.

**Done when:** emergency recall on the synthetic set is at or near 100% (investigate every
miss), every output validates against the schema, and no output contains drug names or doses.

### Phase 3 — Central case store and doctor portal (mentor steps 3 and 4)

**Goal:** cases live in one secure place and a remote doctor can review and respond.

**Concepts:** relational modelling, authentication/authorisation, role-based access, audit
logging, pseudonymisation, background jobs, basic web security (OWASP top issues).

**Tasks:**
1. Postgres schema + migrations for patients, cases, doctors, audit events.
2. Object storage for audio (and later images) with signed, expiring URLs.
3. Auth: separate roles (patient, doctor, admin). Doctors are manually verified in the MVP.
4. Consent screen on the patient side; store what was agreed and when; honour withdrawal.
5. De-identification view: doctors see the clinical content with minimal identity by default.
6. Orchestrator: implement the case state machine as explicit code (not implicit prompts);
   each agent step is a retry-safe job.
7. Doctor portal: queue sorted by triage level then waiting time; case page with transcript,
   audio player, structured symptoms, red flags, AI summary (clearly labelled).
8. Doctor actions: edit summary, request more info (sends a question back to the patient),
   write a recommendation, mark reviewed. Everything logged.
9. Patient view: see the doctor's recommendation in Arabic; emergency cases highlighted.
10. Notifications: simple (email/SMS/WhatsApp-style) when a recommendation is ready; start
    with polling if integrations are heavy.
11. Time-outs and SLAs: if an urgent case waits too long, escalate and alert an admin.
12. Security pass: rate limits, input validation, secrets management, backup/restore test.
13. Doctor feedback capture: thumbs-up/down and corrections on AI summary and triage level
    (this is the best eval data you will ever get).

**Deliverable:** end-to-end demo: patient records -> AI triage -> doctor reviews -> patient
reads the recommendation.

**Done when:** a stranger (e.g. a doctor friend) can use the doctor portal without
explanation on synthetic cases; every state change appears in the audit log; no endpoint
returns another patient's data in tests.

### Phase 4 — Pharmacies (mentor step 5)

**Goal:** a doctor's prescription can reach a pharmacy near the patient.

**Do not start until the legal/ethical questions in section 12 are answered.**

**Concepts:** prescription data modelling, geospatial lookup, integration patterns
(webhook vs polling vs manual), failure handling in multi-party workflows.

**Tasks:**
1. Prescription entry in the doctor portal: doctor types medicines and instructions;
   the AI may only check formatting/completeness, never suggest drugs.
2. Pharmacy directory: name, area, hours, contact; patient chooses a pharmacy or the
   system proposes the nearest few.
3. Delivery channel, simplest first: (a) printable/shareable prescription with a code,
   (b) pharmacy web view with a one-time link, (c) real API/WhatsApp integration later.
4. Pharmacy actions: accept, report out-of-stock, mark fulfilled. Patient is notified.
5. Pharmacy agent (agentic part): given an out-of-stock report, find alternative nearby
   pharmacies and ask the patient to confirm; never substitute medicines on its own.
6. Basic safety checks surfaced to the doctor (not decided by AI): duplicate items, missing
   dose, patient-reported allergies mentioned in the transcript.
7. Audit and tamper-evidence: a prescription cannot be edited after issue; changes create a
   new version.

**Deliverable:** prescription -> pharmacy -> fulfilled flow with at least two mock pharmacies.

**Done when:** an out-of-stock scenario is handled end to end with the patient confirming
the new pharmacy, and every step is logged.

### Phase 5 — Image upload (mentor step 6)

**Goal:** patients can attach photos (rash, wound, swelling, medication box) to a case.

**Concepts:** image compression for weak connections, EXIF/GPS stripping, quality checks,
privacy risks of photos (faces, locations, children).

**Tasks:**
1. Upload UI on the patient side with guidance ("good light, include a coin for scale,
   one photo close and one farther away").
2. Client-side compression and offline queue (reuse Phase 1 machinery).
3. Server: strip EXIF/GPS, virus/size/type checks, store with signed URLs.
4. Quality gate: blur/darkness detection; ask for a retake if too poor.
5. Attach images to cases; show them in the doctor portal with zoom and side-by-side.
6. Consent specific to images; easy deletion.

**Deliverable:** images flow from phone to doctor portal reliably on a weak connection.

**Done when:** a 5 MB phone photo uploads under throttled network conditions, arrives with
metadata stripped, and a blurry photo triggers a retake request.

### Phase 6 — Image-based decision support (mentor step 7)

**Goal:** a model gives the doctor a cautious second opinion on images, never the patient.

**Concepts:** transfer learning, data augmentation, class imbalance, calibration,
out-of-distribution detection, dataset bias (skin tone!), model cards, explainability (e.g.
Grad-CAM).

**Tasks:**
1. Pick ONE narrow task first (e.g. skin lesion triage or wound/infection signs). A narrow,
   honest model beats a broad, unreliable one. Check dataset licences and document them.
2. Public dataset exploration: class balance, image quality, demographic coverage. Write down
   what the dataset cannot represent.
3. Baseline: fine-tune a pretrained backbone; log training with a fixed random seed and
   saved splits (split by patient/lesion, never by image, to avoid leakage).
4. Metrics: per-class recall, confusion matrix, calibration curve; report results by
   subgroup where labels allow it.
5. Uncertainty: add an "unsure / out of scope" output; route low-confidence or
   out-of-distribution images to "doctor decides, no suggestion".
6. Explainability: heatmaps shown to the doctor as a sanity check.
7. Integrate as the Image agent: output = top suggestions + confidence + caveats, shown in
   the doctor portal under a clear "decision support" label.
8. Write a model card: intended use, data, metrics, failure modes, what it must not be used for.
9. Compare against a multimodal LLM baseline if useful; report honestly which is better and
   at what cost.

**Deliverable:** doctor-facing image suggestion with uncertainty, plus a model card.

**Done when:** the model card exists, low-confidence cases are demonstrably withheld, and
the write-up states the limits plainly.

### Phase 7 — Hardening, pilot readiness, and write-up

**Goal:** make the project presentable and honest.

**Tasks:**
1. Reliability: retries, idempotency, backups, load test with 100 concurrent synthetic cases.
2. Cost and latency report per case (ASR + LLM + storage).
3. Security review and a threat model (what if an account is stolen? what if audio leaks?).
4. Failure-mode report: top 10 ways the system can hurt someone and the mitigation for each.
5. Documentation: README, architecture diagram, demo video, setup guide.
6. Academic/portfolio write-up: problem, design, evaluation, limitations, ethics, future work.
7. Optional: small pilot with a doctor/clinic under the mentor's supervision and proper consent.

**Done when:** a stranger can clone the repo, run the demo, and read an honest limitations section.

---

## 9. Evaluation summary

| Component | Headline metric | Notes |
|---|---|---|
| ASR | WER on dialectal, noisy Arabic | track per speaker/noise level |
| Extraction | schema validity + field-level accuracy | null is better than a guess |
| Triage | emergency recall | report every false negative |
| Summary | faithfulness (no invented facts) | hand-check samples; doctor ratings |
| Pharmacy flow | end-to-end success rate in failure scenarios | simulated |
| Vision | per-class recall + calibration | subgroup reporting, OOD rejection |

---

## 10. Conventions

- Type hints, small functions, one agent per file.
- Prompts live in versioned files under `backend/prompts/`, not inline strings.
- Every agent has a schema, a test, and an eval entry.
- Log agent inputs/outputs without personal data so failures can be inspected.
- Record significant decisions as short notes in `docs/decisions/` (what, why, alternatives).
- Commit small; the message says what and why. Never commit secrets, audio, images, or real
  patient data.
- Seed randomness and save dataset splits for reproducibility.

## 11. Progress tracker (Ahmed updates this as he goes)

- [ ] Phase 0 — Study and setup
- [ ] Phase 1 — Voice to transcript
- [ ] Phase 2 — Intake and triage agents
- [ ] Phase 3 — Case store and doctor portal
- [ ] Phase 4 — Pharmacies
- [ ] Phase 5 — Image upload
- [ ] Phase 6 — Image-based decision support
- [ ] Phase 7 — Hardening and write-up

Current phase: Phase 0
Last decision: (fill in)
Next concrete task: (fill in)

## 12. Open questions for the mentor

1. Target users: patients directly, or community health workers on their behalf?
2. Which legal framework covers remote doctors and cross-border prescriptions?
3. Is the first demo for a real pilot, or an academic/portfolio prototype?
4. Which Arabic dialects must be supported first?
5. Is there an existing dataset or partner clinic, or do we build synthetic data?
6. What does "connect with pharmacies" mean concretely: a directory, an order, a stock check?
7. Who verifies doctors, and who is accountable for a bad recommendation?
8. Where is data allowed to be stored (country, provider)?
9. Which one narrow image task should Phase 6 target?
10. What counts as success for the mentor: working demo, paper, pilot, or portfolio?
