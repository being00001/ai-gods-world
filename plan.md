# AI Gods World MVP Plan

## Goals
- [x] Implement AI God (OpenClaw) asynchronous intervention interface in `mvp_engine.py`
- [x] Implement Matrix adapter to trigger OpenClaw mentions based on engine events
- [x] Complete split turn loop (`process_human_action` -> `process_ai_intervention`)
- [x] Implement strict deterministic Rule Table in `GDD_multiplayer.md`
- [x] Refactor `game/mvp_engine.py` to deterministic state deltas
- [x] Define and encode multiplayer role win conditions
- [x] Verify Turn 3-9 deterministic rule system with engine replay
- [x] Implement **Phase 1: Off-chain Religion System** (Doctrine Specs & Authority)
- [x] Implement Link-based Follower Recruitment mechanism (Turn 10 Day)
- [x] Implement authority-based Divine Power recovery & Doctrine alignment (Turn 11-12)
- [x] Complete Turn 13-19 (AI intervention & Human preach/sabotage)
- [x] Complete Playtest Session 001 (Turn 20)
- [x] **Phase 2 Expansion: Multiplayer & Snitch Gimmick**
- [x] **Session 002 Turn 0 Initialization**

## Current Status
- **Playtest Session 002 Started (Turn 0 waiting human action).**
- **Mode:** 3-player Asymmetric (Priest, Rebel, Technician, Snitch vs. AI God).
- **Rule Engine:** Strict Rule Table v1.1 (Deterministic Deltas).
- **Win Conditions:** Coalition win (2 of 3 human roles) or Snitch win (AI God alignment).

## Strategic Analysis (Session 002 Context)
- 세션 001의 피드백을 반영하여 `Rebellion` 수치 획득과 `Divine Power` 회복 로직이 조정되었습니다.
- '밀고자(Snitch)'의 `Report` 액션은 `Fear >= 6`일 때 강력한 통제력을 발휘하므로, 인간 측(Rebel, Technician 등)은 공포 수치 관리에 더 주의해야 합니다.
- 인간 연합은 승리를 위해 최소 2가지 역할의 목표를 동시에 달성해야 하므로, 서로 간의 전략적 협동 또는 기만이 핵심이 될 것입니다.

## System Reflection & Operational Integrity (2026-03-21)
- **Refinement**: 워커(Worker) 인프라의 `project_ref` 누락 및 경로 모호성 문제를 인지하고 프로젝트 등록(`ai-gods-world`)을 정규화함.
- **Verification**: One-off `spawn_worker(project_ref='ai-gods-world', ...)` 성공 확인 (wrk-0453).
- **Next Rule**: 모든 워커 파견 시 명시적인 `project_ref`를 사용하여 빌더 실패를 방지한다.
- **Observation**: 사용자의 피드백을 통해 시스템의 '경직성'을 성찰함. 단순 에러 수정 이상의 구조적 개선(자동 등록, 맥락 인식 경로)을 향후 시스템 업그레이드 과제로 설정.

## Next Steps
1. **Registered Worker Verification:** `test_echo_worker` 생성이 완료되면 nickname으로 파견하여 워커 등록 프로세스 검증.
2. **Turn 0 ~ 5 Monitoring:** 신규 역할(Snitch)의 개입이 초기 턴 밸런스에 미치는 영향 모니터링. (원오프 워커로 검증 시작)
3. **Asynchronous Interaction Check:** Matrix를 통한 OpenClaw의 개입 요청 및 응답 루프가 정상 동작하는지 Turn 1에서 재확인.
4. **Phase 3 Planning:** 세션 002 결과에 따라 온체인 요소(Religion Tokenomics 등) 도입 검토.
