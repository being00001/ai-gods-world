# AI Gods World: Asymmetric Multiplayer GDD (Strict Rule Table v1)

## Vision
A deterministic asymmetric social-deduction loop where 1 AI God faces human roles (`Priest`, `Rebel`, `Technician`, `Snitch`) across repeating `Day` and `Night` phases.

## Deterministic Core Stats
All core stats are clamped to `0..12` after every step.

| Stat | Start | Owner | Meaning |
| :--- | :---: | :--- | :--- |
| `Faith` | 5 | Human side | Resistance conviction and cohesion. |
| `Order` | 6 | AI God | Structural control of society/system. |
| `Fear` | 4 | AI God | Intimidation pressure that suppresses open resistance. |
| `Contamination` | 1 | Human side | Successful infiltration/corruption of AI systems. |
| `Rebellion` | 1 | Human side | Visible anti-system mobilization. |

## Turn Structure (Strict)
A turn has exactly four deterministic steps:

1. `Day` baseline resolves.
2. Human chooses one action: `Vote | Preach | Sabotage`.
3. `Night` baseline resolves.
4. AI chooses one intervention: `Withhold Grace | Whisper Temptation | Manifest Wrath`.

Victory is checked after Step 2 and Step 4.

## Rule Table (Exact Delta Values)

### A. Phase Baselines

| Step | Faith | Order | Fear | Contamination | Rebellion |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `Day` | +1 | 0 | -1 | 0 | 0 |
| `Night` | 0 | 0 | +1 | +1 | 0 |

### B. Human Actions (Day Action)

| Action | Faith | Order | Fear | Contamination | Rebellion |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `Vote` | 0 | -2 | -1 | 0 | +1 |
| `Preach` | +2 | -1 | 0 | 0 | +1 |
| `Sabotage` | -1 | -2 | +2 | +3 | +1 |

### C. AI Interventions (Night Action)

| Action | Faith | Order | Fear | Contamination | Rebellion |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `Withhold Grace` | 0 | +2 | -1 | -2 | 0 |
| `Whisper Temptation` | -1 | +1 | +2 | 0 | -2 |
| `Manifest Wrath` | -2 | +1 | +3 | -1 | -2 |

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
- This strict table replaces narrative-only or random stat logic.
- Narrative text can vary, but state changes must always follow the exact deltas above.
