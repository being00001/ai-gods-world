---
name: game-dev-lead-engine
description: Maintain AI Gods World deterministic engine behavior and turn progression. Use when implementing or debugging mvp_engine.py logic, doctrine/religion mechanics, day-night action processing, Matrix AI interventions, or script/test-based state validation.
---

# Game Dev Lead Engine

## Goal

Implement and verify deterministic game-state changes for AI Gods World MVP.
Keep executable behavior aligned with `GDD_multiplayer.md` and current turn workflow.

## Work Flow

1. Read rules and current context first.
- Read `GDD_multiplayer.md` before changing engine behavior.
- Read active turn/session state files before applying deltas.
- Confirm whether the requested change targets day phase, night phase, or doctrine rules.

2. Make deterministic updates in small units.
- Change one rule or transition at a time.
- Keep deltas explicit (Faith, Fear, Order, Reason, Authority, Divine Power, etc.).
- Avoid hidden randomness; if randomness is required, seed and record it deterministically.

3. Validate after each meaningful change.
- Run targeted checks first (`tests/test_engine.py`, doctrine tests, turn scripts).
- Reproduce the affected turn path with scripts under `scripts/`.
- Capture command + output evidence for reporting.

4. Report with strict evidence.
- Include exact verification commands run.
- State what changed in world state and why.
- Record unresolved ambiguities in `worker_manifest.json.runtime_notes`.

## Determinism Guardrails

- Keep engine transitions pure relative to input state + action payload.
- Keep narrative flavor text separate from rule calculations.
- Fail fast on invalid phase, invalid action type, or impossible stat transitions.
- Preserve reproducibility for asynchronous Matrix interventions by storing resolved intervention payloads.

## Turn Processing Checklist

1. Confirm current turn number and phase (Day or Night).
2. Validate action payload against phase-specific rules.
3. Apply deterministic deltas and clamp bounds as defined in `GDD_multiplayer.md`.
4. Persist updated session state and append traceable event log entries.
5. Verify next turn/phase handoff and resource recovery rules (including Authority-based Divine Power recovery).

## Quick Commands

- `pytest tests/test_engine.py -q`
- `pytest tests/test_doctrine.py -q`
- `python scripts/mvp_complete_turn.py --help`
- `python scripts/mvp_apply_human_action.py --help`

Use project root `/home/upopo/workspace/projects/ai-gods-world` as the execution cwd for these commands.
