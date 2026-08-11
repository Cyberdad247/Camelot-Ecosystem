# Camelot Apex OS — Control Plane Package
#
# Modules are organized into subdirectories:
#   core/     — gate, governance, HITL (anya_gate, factory_lane, soul_oversight, ...)
#   dispatch/ — routing, dispatch, agent management (bifrost, switchboard, ...)
#   runes/    — runic commands, CLI, TOON (runic_router, camelot_cli, ...)
#   infra/    — infrastructure, memory, sync, observability, bridges, phase_h, ...
#   cluster/  — swarm daemons (agents_daemon, consensus_daemon, ...)
#
# Import modules by their real path:
#
#     from control_plane.core.anya_gate import AnyaGate
#     from control_plane.infra.kinetic_loop import KineticLoop
#
# ─────────────────────────────────────────────────────────────────────────────
# HISTORY: this file used to install a sys.meta_path finder that redirected
# ``control_plane.<name>`` to ``control_plane.<subdir>.<name>``, so that code
# written before the reorganisation kept working. It was removed on 2026-08-11
# because it caused two classes of silent bug:
#
#   1. It decoupled import paths from filesystem paths. Modules kept importing
#      after the move while every hand-counted ``Path(__file__).parent.parent``
#      chain silently began resolving one level short — governance code read and
#      wrote phantom directories under control_plane/03_VAULT for weeks, and a
#      second divergent provenance ledger accumulated there.
#
#   2. It loaded each module TWICE, under both names. Module-level state was
#      duplicated (an lru_cache populated via one name was invisible via the
#      other) and identity comparisons failed: a TriageScore built from
#      ``control_plane.core.factory_lane`` was rejected by a pydantic model that
#      referenced ``control_plane.factory_lane``, because those were genuinely
#      different classes.
#
# Import errors are noisier than a redirect, but they point at the truth.
# Do not reintroduce the finder. If a module moves, update its importers.
# ─────────────────────────────────────────────────────────────────────────────
