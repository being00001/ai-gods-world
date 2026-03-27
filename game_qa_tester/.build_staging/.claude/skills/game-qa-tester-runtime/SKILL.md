---
name: game-qa-tester-runtime
description: Deterministic QA workflow for AI Gods World gameplay, turn processing, and UI or CLI behavior. Use when tasks require playtesting, browser simulation, regression checks, bug reports, balance validation, or pass or block QA recommendations.
---

# Game QA Tester Runtime

## Overview
Run deterministic QA passes for AI Gods World and produce evidence-driven bug or sign-off reports.

## Workflow
1. Read task context artifacts and extract active turn, phase, and acceptance checks.
2. Confirm path/write policy and execute project commands from `/home/upopo/workspace/projects/ai-gods-world`.
3. Use `GDD_multiplayer.md` as the deterministic rules source when validating outcomes.
4. Run targeted reproduction first for the specific feature or flow under test.
5. Run broader end-to-end playthrough checks for regression confidence.
6. Record evidence for each finding: command/input, observed output, expected output, and severity.
7. End with at least one explicit verification command tied to acceptance.

## QA Coverage
- Turn progression integrity across Day -> Night -> next Day.
- World stat updates after human or AI actions.
- UI/UX clarity, interaction friction, and broken flows.
- CLI command correctness and failure-path handling.
- Gameplay balance anomalies and exploit paths.

## Reporting Rules
- Keep findings reproducible and prioritized by severity.
- Flag blockers and missing interfaces instead of guessing.
- Include a clear pass/block recommendation for tested scope.
