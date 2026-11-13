# ASR eval set

Phase 0 target: 10 clips. Phase 1 target: 30+.

- Audio goes in `evals/asr/audio/` — **git-ignored**, never committed (it is your voice).
- One row per clip in `manifest.csv`. The hand-written reference transcript is the ground truth.

Columns:
- `clip_id` — e.g. `p0_001`
- `file` — filename inside `audio/`
- `speaker` — pseudonym, e.g. `S1`
- `dialect` — e.g. `gaza`, `levantine`
- `noise` — `quiet` | `noisy`
- `reference` — exact transcript, written by hand

## WER results

| Date | Model | Clips | WER (quiet) | WER (noisy) | WER (all) | Notes |
|---|---|---|---|---|---|---|
