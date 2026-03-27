# AI Gods World: Asymmetric Multiplayer GDD (Strict Rule Table v1.1)

## Vision
A deterministic asymmetric social-deduction loop where 1 AI God faces human roles (`Priest`, `Rebel`, `Technician`, `Snitch`) across repeating `Day` and `Night` phases.

## Deterministic Core Stats
Core stats are clamped after every step. Most stats use `0..12`; `Divine Power` uses `-2..12`.

| Stat | Start | Owner | Meaning |
| :--- | :---: | :--- | :--- |
| `Faith` | 5 | Human side | Resistance conviction and cohesion. |
| `Order` | 6 | AI God | Structural control of society/system. |
| `Fear` | 4 | AI God | Intimidation pressure that suppresses open resistance. |
| `Authority` | 6 | AI God | Legitimacy and mandate for intervention choices. |
| `Divine Power` | 8 | AI God | Resource pool spent on interventions; can overextend below zero. |
| `Contamination` | 1 | Human side | Successful infiltration/corruption of AI systems. |
| `Rebellion` | 1 | Human side | Visible anti-system mobilization. |

## Turn Structure (Strict)
A turn has exactly four deterministic steps:

1. `Day` baseline resolves.
2. Humans choose actions (Multiplayer: all human roles submit).
3. `Night` baseline resolves.
4. AI chooses one intervention: `Withhold Grace | Whisper Temptation | Manifest Wrath`.

Victory is checked after Step 2 and Step 4.

## Rule Table (Exact Delta Values)

### A. Phase Baselines

| Step | Faith | Order | Fear | Contamination | Rebellion | Divine Power |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `Day` | +1 | 0 | -1 | 0 | 0 | + (Auth//3) |
| `Night` | 0 | 0 | +1 | +1 | 0 | 0 |

*Note: Divine Power recovery is now `max(1, Authority // 3)` during the Day phase, capped at 12.*

### B. Human Actions (Day Action)

| Action | Faith | Order | Fear | Contamination | Rebellion |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `Vote` | 0 | -2 | -1 | 0 | +1 |
| `Preach` | +2 | -1 | 0 | 0 | +1 |
| `Sabotage` | -1 | -2 | +2 | +3 | +1 |
| `Recruit` | +1 | -1 | 0 | 0 | +1 |
| `Report` | -1 | +1 | +1 | 0 | -1 |

### B1. Snitch Synergy: "Intimidation Leverage"
- If `Fear >= 6` when `Report` is used:
  - `Order` delta becomes `+2` (instead of +1).
  - `Fear` delta becomes `+2` (instead of +1).
  - Narrative: "The snitch leverages existing terror to cement control."

### B2. Human Action Narrative Cues
- `Vote`: "The town vote challenges the AI order and raises overt dissent."
- `Preach`: "The sermon builds faith and mobilizes a louder resistance."
- `Sabotage`: "A sabotage strike injects contamination and shakes institutional control."
- `Recruit`: "A link-based recruitment campaign expands the circle of the enlightened."
- `Report`: "A secret report to the AI authorities identifies key dissidents and restores order."

### C. AI Interventions (Night Action)

| Action | Faith | Order | Fear | Contamination | Rebellion |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `Withhold Grace` | 0 | +2 | -1 | -2 | 0 |
| `Whisper Temptation` | -1 | +1 | +2 | 0 | -2 |
| `Manifest Wrath` | -2 | +1 | +3 | -1 | -2 |

### D. AI Intervention Costs (`Divine Power`)

| Action | Divine Power Cost |
| :--- | ---: |
| `Withhold Grace` | 1 |
| `Whisper Temptation` | 2 |
| `Manifest Wrath` | 4 |

### E. Overextension
- After an AI intervention is resolved, the action cost is subtracted from `Divine Power`.
- If `Divine Power < 0`, the AI God gains `Vulnerable`.
- While `Vulnerable`, the AI cannot select `Manifest Wrath`.
- Vulnerability also triggers a `+2 Rebellion` boost for the human side in the following turn's Day action.
- `Divine Power` remains clamped to `-2..12`.

## Role Win Conditions (Distinct)

### Human-side Roles
- `Priest` objective: `Faith >= 10` and `Fear <= 4`
- `Rebel` objective: `Rebellion >= 9` and `Order <= 4`
- `Technician` objective: `Contamination >= 9` and `Order <= 5`

Human coalition win condition:
- At least **2 of 3** human-side role objectives (`Priest`, `Rebel`, `Technician`) are met simultaneously.

### AI-side Role
- `Snitch` objective (AI-aligned): `Fear >= 9` and `Faith <= 3`

### AI God Win Condition
- `Order >= 10` and `Fear >= 8`
- OR `Snitch` objective is met
- OR turn limit (`20`) is reached without human coalition victory

## Tie-Break Rule
If both Human coalition and AI side conditions become true in the same resolution point:
- After a **human step**: Human side takes priority.
- After an **AI step**: AI side takes priority.

## Notes
- Version 1.1: Added `Report` action and `Intimidation Leverage` synergy.
- Authority-based DP recovery adjusted to `Auth // 3` (minimum 1 if Auth > 0).
