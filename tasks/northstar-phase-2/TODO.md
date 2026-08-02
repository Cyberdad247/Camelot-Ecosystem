# TODO: Northstar Phase 2 Work Breakdown

Decomposed from `PLAN.md` into actionable tasks.

- [ ] **Milestone 1: Bifrost Public Gateway & mTLS Roaming** `[security] [backend]`
  - [ ] Add optional client certificate verification (mTLS) to FastAPI server in `control_plane/bifrost.py`
  - [ ] Implement bearer token verification as an alternative authentication path
  - [ ] Refactor subnet checking in `bifrost.py` to allow validated roaming IPs
- [ ] **Milestone 2: Dynamic Knight Swapping & Intent Switchboard** `[backend]`
  - [ ] Update `omnivoice-router.ts` WebSocket message protocol to accept a target `knight_id` `[parallel]`
  - [ ] Implement keyword extraction in `audio_session.py` to route context dynamically to specific Knights
  - [ ] Refactor Kokoro chunk generation in `kitten_service.py` to dynamically swap voice models `[parallel]`
- [ ] **Milestone 3: Delta-Sync Payload Compression** `[backend]`
  - [ ] Implement `TOON_v2_diff` serialization to only send UI and coordinate state differences
  - [ ] Enable binary or text gzip compression on WebSocket connections in `edge-router.ts`
- [ ] **Milestone 4: Verification & Integration Testing** `[test]`
  - [ ] Add E2E simulation cases in `scripts/start_northstar.py` to mock public gateway connections
  - [ ] Add verification tests for mid-dialogue Knight hot-swapping
  - [ ] Log packet sizes to assert delta compression ratio (>60% reduction)
