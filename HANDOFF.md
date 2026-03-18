# AI Gods World - Handoff Protocol

**Purpose**: Enable any developer (human or AI) to pick up where the last cycle left off.

---

## Current Cycle: 2026-03-19 (Cycle 0 - Emergency Stabilization)

### What Was Done
1. **Diagnosed "unplayable" report** - Full code review of backend (engine.py, entities.py, web_server.py) and frontend (app.js, index.html)
2. **Fixed 3 critical bugs**:
   - Removed CSRF enforcement that blocked all POST API calls
   - Fixed `divine_power` key mismatch in frontend resource display
   - Added timestamps to game events
3. **Removed unused dependencies**: flask-wtf, wtforms
4. **Created ROADMAP.md**: 4-phase development plan with milestones
5. **Created this HANDOFF.md**: Continuity protocol

### Decisions Made & Rationale
| Decision | Rationale | Alternative Considered |
|----------|-----------|----------------------|
| Remove CSRF entirely (not just exempt API routes) | API is JSON-based, no form submissions. CSRF via headers would add complexity for zero users. | Could add X-CSRF-Token header flow later if needed |
| Keep single shared game state for now | No user accounts yet. Session-based state is Phase 1 work. | Could have added Flask sessions immediately |
| Didn't add tests | Emergency stabilization; tested manually via Python REPL | Phase 1 should add pytest suite |

---

## Next Cycle Action Items

### Immediate (Next Session)
1. **Commit and push fixes** to GitHub → trigger Render redeploy
2. **Verify live site** works: test all 6 actions (recruit, attack, pray, miracle, build, advance turn)
3. **Check QA tester (wrk-0151) report** and cross-reference with fixes

### Phase 1 Sprint (Next 1-2 Cycles)
1. Implement session-based game state (Flask sessions + per-session GameEngine)
2. Add passive resource generation in `process_turn()`
3. Implement building effects in `_process_building_effects()`
4. Basic AI: make enemy deities take random actions each turn

---

## Architecture Notes

### File Structure
```
ai-gods-world/
├── game/
│   ├── __init__.py        # Package init
│   ├── engine.py          # GameEngine, GameState, turn processing, all game actions
│   ├── entities.py        # Entity-Component system (Deity, Follower, Region, Building, Unit)
│   └── web_server.py      # Flask app, REST API endpoints
├── static/
│   ├── app.js             # Frontend: API client, UI updates, form handlers
│   └── style.css          # Styling
├── templates/
│   └── index.html         # Main game page (single-page app)
├── requirements.txt       # Python deps (flask, gunicorn)
├── render.yaml            # Render.com deployment config
└── vercel.json            # Vercel config (not actively used)
```

### Key Patterns
- **Entity-Component System**: All game objects (deities, followers, buildings) are `Entity` with attached `Component` classes
- **Single GameEngine instance** at module level in web_server.py (shared across all requests)
- **REST API**: All game actions are POST to `/api/<action>`, state is GET `/api/state`
- **No database**: All state is in-memory, lost on restart
- **Frontend polling**: app.js polls `/api/state` every 10 seconds

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/state` | Full world state |
| GET | `/api/balance/<deity_id>` | Deity resources |
| GET | `/api/followers/<deity_id>` | Deity followers |
| GET | `/api/events` | Event log |
| POST | `/api/recruit` | Recruit followers |
| POST | `/api/attack` | Attack enemy |
| POST | `/api/pray` | Pray for resources |
| POST | `/api/build` | Build structure |
| POST | `/api/miracle` | Perform miracle |
| POST | `/api/turn` | Advance turn |

---

## Feedback Loop Protocol

For each development cycle:

```
1. READ this handoff + ROADMAP.md
2. CHECK current deployment status (is the site up?)
3. REVIEW any user feedback / QA reports
4. PICK highest-priority items from roadmap
5. IMPLEMENT with tests
6. VERIFY on live site
7. UPDATE this handoff with:
   - What was done
   - Decisions made & rationale
   - Next cycle action items
8. COMMIT and PUSH
```

---

## Key Metrics to Track

| Metric | Current Value | Target (Phase 1) | How to Measure |
|--------|--------------|-------------------|----------------|
| Actions that work | 6/6 (after fix) | 6/6 | Manual test each action |
| Game completable | No (AI passive) | Yes | Play through to victory |
| Mobile playable | Partial | Yes | Test on phone browser |
| Avg game length | N/A | 10-15 min | Playtest |
| Unique players | ~0 | 10+ | Analytics (Phase 3) |
