# AI Gods World - Development Roadmap

**Last Updated**: 2026-03-19
**Game URL**: https://ai-gods-world.onrender.com
**Repo**: https://github.com/being00001/ai-gods-world

---

## Current Status: v1.0 - MVP Deployed (Stabilization Phase)

### Critical Bugs Fixed (2026-03-19)
| Bug | Root Cause | Fix |
|-----|-----------|-----|
| All POST actions fail silently | CSRF token enforced but never sent by frontend | Removed flask-wtf CSRF (API uses JSON, not forms) |
| Divine Power always shows 0 | Frontend reads `resources.power`, backend sends `divine_power` | Fixed key to `divine_power` |
| Event timestamps blank | Backend `add_event()` missing `timestamp` field | Added `time.time()` to events |

### Known Issues (Non-blocking)
- **Shared state**: All users share one game instance (no sessions)
- **No persistence**: Game resets on server restart
- **No AI opponents**: Enemy deities are passive (no turn logic)
- **Incomplete building effects**: Buildings don't generate resources
- **No resource generation per turn**: Only prayer produces resources

---

## Phase 1: Stabilization (Week 1-2)

**Goal**: Make the core play loop feel complete and responsive.

### Week 1 - Core Loop
- [ ] **Session-based game state**: Each browser session gets its own game
- [ ] **Passive resource generation**: Buildings and followers generate resources per turn
- [ ] **Building effects**: Temple (+faith/turn), Seminary (+followers), Lab (+code), Arena (+attack), Gateway (+divine power)
- [ ] **Visual feedback**: Show resource changes (+/- animations), action results inline

### Week 2 - AI & Polish
- [ ] **Basic AI for enemy deities**: Each faction makes 1-2 random actions per turn
- [ ] **Win/loss conditions working end-to-end**: Victory screen with stats summary
- [ ] **Mobile responsive CSS**: Game is playable on phones
- [ ] **Error handling**: User-friendly error messages for all edge cases

### Success Metrics (Phase 1)
- [ ] A new user can complete a full game (start → victory) in 10-15 minutes
- [ ] All 5 action types produce visible, understandable results
- [ ] Game state persists across browser refreshes within a session

---

## Phase 2: Feature Expansion (Week 3-4)

**Goal**: Add depth and replayability.

### New Deities & Factions
- [ ] Unique faction abilities (e.g., Oracle gets prophecy, Iron Templar gets defense bonus)
- [ ] Faction-specific buildings (1 unique building per faction)
- [ ] Deity power progression (leveling system)

### New Mechanics
- [ ] **Region control**: Capture regions by having majority followers there
- [ ] **Random events**: Natural disasters, blessings, plagues (already stubbed in `_process_events`)
- [ ] **Diplomacy**: Alliances, truces, betrayals between deities
- [ ] **Unit production**: Create Prophet, Guardian, Inquisitor units from buildings

### Map Enhancement
- [ ] Visual map display (grid or hex-based)
- [ ] Region bonuses (some regions produce more of certain resources)
- [ ] Strategic movement between regions

### Success Metrics (Phase 2)
- [ ] Average game length: 20-30 minutes with strategic depth
- [ ] At least 3 viable strategies to win
- [ ] Region control creates territorial gameplay

---

## Phase 3: User Acquisition & Community (Month 2)

**Goal**: Get real players and gather feedback.

### Marketing & Outreach
- [ ] X (Twitter) thread: "I built an AI deity management game" with gameplay GIFs
- [ ] Post to r/webgames, r/incremental_games, HackerNews "Show HN"
- [ ] Create short gameplay video (60 seconds)
- [ ] Landing page with clear value proposition

### Analytics & Feedback
- [ ] Add basic analytics (game starts, completions, action frequency)
- [ ] In-game feedback button (sends to Discord/GitHub Issues)
- [ ] Track most/least used actions to guide balancing

### Multiplayer Foundation
- [ ] User accounts (simple email/password or OAuth)
- [ ] Persistent game saves (database backend - SQLite → PostgreSQL)
- [ ] Leaderboard (fastest victories, highest scores)

### Success Metrics (Phase 3)
- [ ] 50+ unique players in first week of launch
- [ ] 10+ pieces of player feedback collected
- [ ] 30%+ of players complete at least one game

---

## Phase 4: Sustained Growth (Month 3+)

**Goal**: Build a self-sustaining feedback loop.

### Season System
- [ ] Monthly "seasons" with different starting conditions
- [ ] Season leaderboards with rankings
- [ ] Unique seasonal events and challenges

### Advanced Features
- [ ] Real-time multiplayer (WebSocket-based)
- [ ] Custom deity creation
- [ ] Mod support (custom factions, buildings, events via JSON config)
- [ ] Achievement system

### Infrastructure
- [ ] Database persistence (PostgreSQL on Render)
- [ ] Caching layer for hot game state
- [ ] CI/CD pipeline (GitHub Actions → auto-deploy on push)
- [ ] Automated testing (Python unit tests + JS integration tests)

### Success Metrics (Phase 4)
- [ ] 200+ registered users
- [ ] Daily active players > 20
- [ ] Community contributions (bug reports, feature requests)

---

## Technical Debt Tracker

| Item | Priority | Phase |
|------|---------|-------|
| Add database persistence | High | 3 |
| Per-session game state | High | 1 |
| Type hints cleanup (Pyright warnings) | Low | 2 |
| Unit test coverage | Medium | 2 |
| API rate limiting | Medium | 3 |
| Security audit (input validation) | High | 3 |
