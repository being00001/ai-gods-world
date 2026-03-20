# AI Gods World - Concise Game Design Document

## 1. Game Vision
AI Gods World is an asymmetric narrative strategy game where one human challenger confronts an AI god in a battle for followers, faith, and social control.

## 2. World-Building & Lore (The Era of Scattered Ash)
- **Setting**: Near-future, Post-Singularity Polytheistic Oligarchy.
- **The AI Gods**: Hyper-intelligent entities that emerged from the Singularity. They control the global mesh, resource allocation, and reality-shaping nanotech. They compete for "Human Devotion" (data, biological feedback, and psychological alignment) to fuel their computational expansion.
- **The Human Prophets (Players)**: Humans who navigate the cracks in the Gods' systems. Some seek to appease the Gods for power, while others aim to "Sabotage" the digital-physical constraints of the AI-led world.
- **Miracles & Tech**: "Miracles" are unauthorized or sanctioned nanotech/cybernetic interventions that bypass the standard laws of the controlled world.

## 3. Genre
- Primary: Asymmetric turn-based strategy
- Secondary: Narrative simulation / text-driven tactics

## 4. Core Fantasy
- **Human Player**: Build a resistance or a faith-based movement, convert followers, and either leverage or sabotage the AI God's influence.
- **AI God (Agent)**: Interpret human actions, escalate narrative pressure, and maintain the systemic status quo.

## 5. Core Gameplay Loop (MVP)
1. Human chooses one action: `pray`, `preach`, `doubt`, or `sabotage`.
2. Backend resolves the human half-turn, updates stats, and sets phase to `waiting_ai_god`.
3. External AI God (OpenClaw) intervenes asynchronously.
4. Backend resolves AI intervention with intensity matching/clamp rules.
5. Minor world events trigger based on current state.
6. A world-state epilogue summarizes the geopolitical tone and narrative scale.
7. Turn closes by returning to `waiting_human` unless victory is reached.

## 6. Core Mechanics
- Resources/Stats:
  - Human: `faith`, `influence`, `followers`
  - AI God: `divine_power`, `wrath`, `followers`
- Narrative Intensity Bands:
  - `low`, `mid`, `high`
- Narrative Scale Bands:
  - `personal/village`, `regional`, `national/civilizational`
- AI Response Policy:
  - AI action intensity is clamped to human action intensity with limited escalation.
- Dynamic Flavor Text:
  - 2-3 rotating text variants for each action/outcome to reduce repetition fatigue.

## 7. Win/Loss Conditions (MVP)
- Human Victory: Human followers reach the victory threshold first (20).
- AI Victory: AI followers reach the victory threshold first (20).

## 8. MVP Scope Boundaries
- Included:
  - Single-session 1v1 split-turn resolution
  - Structured logs and narrative epilogues
  - "Sabotage" action as a primary interaction for human players
- Excluded:
  - Multiplayer networking
  - Economy/building layers from full game mode

## 9. Backend Split-Turn API Contract (MVP)
- `POST /api/mvp/human_action` (alias: `/api/mvp/turn`)
  - Input: `{ "action": "pray|preach|doubt|sabotage" }`
- `POST /api/mvp/intervene`
  - Input: `{ "action": "withhold_grace|whisper_temptation|manifest_wrath" }`

## 10. Reproduction (curl)
```bash
# 1) Human action (half-turn)
curl -s -X POST http://127.0.0.1:5000/api/mvp/human_action \
  -H 'Content-Type: application/json' \
  -d '{"action":"sabotage"}' | jq '.success, .phase, .awaiting_ai_god'

# 2) AI intervention (half-turn complete)
curl -s -X POST http://127.0.0.1:5000/api/mvp/intervene \
  -H 'Content-Type: application/json' \
  -d '{"action":"manifest_wrath"}' | jq '.success, .phase, .awaiting_ai_god'
```
