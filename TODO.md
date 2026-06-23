# TODO: Northstar Phase 2 Work Breakdown

Decomposed from `PLAN.md` into actionable tasks.

- [x] **Milestone 1: Bifrost Public Gateway & mTLS Roaming** `[security] [backend]`
  - [x] Add optional client certificate verification (mTLS) to FastAPI server in `control_plane/bifrost.py`
  - [x] Implement bearer token verification as an alternative authentication path
  - [x] Refactor subnet checking in `bifrost.py` to allow validated roaming IPs
- [x] **Milestone 2: Dynamic Knight Swapping & Intent Switchboard** `[backend]`
  - [x] Update `omnivoice-router.ts` WebSocket message protocol to accept a target `knight_id`
  - [x] Implement keyword extraction in `audio_session.py` to route context dynamically to specific Knights
  - [x] Refactor Kokoro chunk generation to dynamically swap voice models (e.g. `af_heart` to `am_adam`)
- [x] **Milestone 3: Delta-Sync Payload Compression** `[backend]`
  - [x] Implement `TOON_v2_diff` serialization to only send UI and coordinate state differences
  - [x] Enable binary or text gzip compression on WebSocket connections in `edge-router.ts`
- [x] **Milestone 4: Verification & Integration Testing** `[test]`
  - [x] Add E2E simulation cases in `scripts/start_northstar.py` to mock public gateway connections
  - [x] Add verification tests for mid-dialogue Knight hot-swapping
  - [x] Log packet sizes to assert delta compression ratio (>60% reduction)

