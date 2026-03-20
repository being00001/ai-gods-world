# AI Gods World MVP Plan

## Goals
- [x] Implement AI God (OpenClaw) asynchronous intervention interface in `mvp_engine.py`
- [x] Implement Matrix adapter to trigger OpenClaw mentions based on engine events
- [x] Add narrative text variations to reduce repetition fatigue
- [x] Complete split turn loop (`process_human_action` -> `process_ai_intervention`)
- [x] Implement strict deterministic Rule Table in `GDD_multiplayer.md`
- [x] Refactor `game/mvp_engine.py` to deterministic state deltas (`Day/Night`, `Vote/Preach/Sabotage`, AI interventions)
- [x] Define and encode multiplayer role win conditions (`Priest`, `Rebel`, `Technician`, `Snitch`)
- [x] Verify Turn 3 deterministic rule system with engine replay (PASS: Faith 6/Order 5/Fear 9/Contamination 4/Rebellion 0)

## Current Status
- `GDD_multiplayer.md` deterministic rule table is verified and functional.
- AI (Snitch role) is reaching win condition (Fear >= 9) faster than human roles in current test scenarios.
- **Engine `awaiting_ai_god` KeyError resolved.** Split-turn loop (Human -> AI -> Next Turn) verified with `scripts/mvp_split_turn_demo.py`.
- Engine now supports explicit role-based win conditions.

## Open Questions
- [x] UI/API label migration: Yes, migrate `pray` -> `vote`, `doubt` -> `sabotage` in the next iteration for consistency with the rule table.
- [AI God Interventions]: For MVP, we'll keep them manual (via Matrix/OpenClaw). For prod, we'll implement a deterministic fallback policy.

## Next Steps
1. **[Current Focus] Engine Test Suite:** Add focused tests for each action delta and each role win condition in `tests/test_engine.py`.
2. **Payload Sync:** Update `game/web_server.py` and frontend labels to match strict rule-table names (`VOTE`, `PREACH`, `SABOTAGE`).
3. **Matrix Update:** Update Matrix playtest scripts to consume the new `stats`/`roles` payload fields.
