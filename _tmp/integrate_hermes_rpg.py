# -*- coding: utf-8 -*-
"""Integrate HERMES_PRIME into the Knight RPG database + system verification artifact."""
import json
import re
from datetime import datetime, timezone

def detect_indent(raw: str) -> int:
    m = re.search(r'\n(\s+)"', raw)
    if m:
        return len(m.group(1))
    return 2

# --- knight_rpg_database.json ---
db_path = 'vfs/knight_rpg_database.json'
raw = open(db_path, encoding='utf-8').read()
db = json.loads(raw)

entry = {
    "knight_id": "HERMES_PRIME",
    "title": "MetaCompiler Forager",
    "level": 1,
    "xp": 0,
    "xp_to_next_level": 100,
    "primary_stat": "Information Synthesis",
    "rune": "\u16B1",
    "skill_graph_tier": "S3 Contextual",
    "ocean_vector": {
        "openness": 0.98,
        "conscientiousness": 0.99,
        "extraversion": 0.85,
        "agreeableness": 0.2,
        "neuroticism": 0.02
    },
    "tasks_completed": 0,
    "last_active": datetime.now(timezone.utc).isoformat(),
}

new_db = {}
for k, v in db.items():
    new_db[k] = v
    if k == 'SIR_HERMES':
        new_db['HERMES_PRIME'] = entry

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(new_db, f, indent=detect_indent(raw), ensure_ascii=False)
    f.write('\n')
print(f"RPG db: inserted HERMES_PRIME after SIR_HERMES ({len(new_db)} knights total)")

# --- system_verification_v1000.json ---
sv_path = 'vfs/system_verification_v1000.json'
sv_raw = open(sv_path, encoding='utf-8').read()
sv = json.loads(sv_raw)
roster = sv.get('knight_rpg_roster', {})
roster['total_knights_registered'] = len(new_db)
roster['classes_count'] = len(new_db)
sample = roster.setdefault('sample_roster', {})
sample['HERMES_PRIME'] = 'MetaCompiler Forager'
sv['knight_rpg_roster'] = roster
with open(sv_path, 'w', encoding='utf-8') as f:
    json.dump(sv, f, indent=detect_indent(sv_raw), ensure_ascii=False)
    f.write('\n')
print(f"system_verification: totals -> {len(new_db)}, sample_roster + HERMES_PRIME")
