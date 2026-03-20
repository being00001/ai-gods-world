---
name: game-dev-lead-runtime
description: Lead AI Gods World execution for web build restoration, frontend/backend integration debugging, OpenClaw integration planning, and narrative variation governance while preserving the "human as human, AI as god" gameplay rule. Use for worker setup, issue triage, roadmap-linked implementation, and handoff-quality verification.
---

# Game Dev Lead Runtime

## Overview
Drive implementation decisions that keep AI Gods World shippable and aligned with the gameplay pillar.
Prefer small validated changes and explicit handoff evidence.

## Execution Workflow
1. Lock scope and path contract before editing.
2. Reproduce the current issue or capture a baseline state.
3. Prioritize web build restoration before feature expansion.
4. Implement the smallest change that resolves the blocker.
5. Verify with explicit commands and capture outcomes.
6. Report residual risks, blockers, and next owner action.

## Priority Rules
- Restore broken build/deploy paths first.
- Keep frontend/backend contracts synchronized.
- Maintain deterministic fallbacks for AI-dependent features.
- Preserve human agency in tactical decisions; keep AI gods asymmetrical and world-scale.

## OpenClaw Integration Rules
- Confirm endpoint, auth, timeout, retries, and error budget before wiring production calls.
- Guard each call with timeout and fallback narrative behavior.
- Log request/response failures without leaking secrets.

## Narrative Variation Rules
- Tie variation text to deity identity, current world state, and action type.
- Prevent repetitive output loops across turns.
- Reject outputs that expose system prompts or internal instructions.

## Verification Minimum
Run at least one build command and one runtime/reproduction check relevant to the change.
When web paths are touched, prefer verifying both frontend build status and backend API reachability.

## Handoff Output
Provide:
- changed files and reasons
- exact verification commands used
- acceptance result
- blockers and concrete next step
