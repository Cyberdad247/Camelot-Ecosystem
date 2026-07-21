# Knowledge Pyramid — Quick Start (5 Minutes)

**Goal**: Get the pyramid running in 5 minutes.

---

## Step 1: Install Dependencies (2 min)

```bash
pip install aiofiles pyyaml sentence-transformers qdrant-client
```

Verify:
```bash
python -c "
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import aiofiles
print('✓ All dependencies installed')
"
```

---

## Step 2: Start Qdrant (1 min)

**Option A: Docker** (Recommended)
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

**Option B: Local binary**
```bash
# Download from https://github.com/qdrant/qdrant/releases
./qdrant --storage-path ./qdrant_storage
```

**Verify**: `curl http://localhost:6333/health`

---

## Step 3: Initialize Knight Directories (1 min)

```python
# Create 03_VAULT/knights/<knight_id>/ directories with stub files
python -c "
import asyncio
from control_plane.knight_knowledgebase import get_knowledgebase

async def init():
    kb = get_knowledgebase()
    knights = ['sir_boris', 'sir_helio', 'sir_ghost', 'sir_hermes']
    for knight_id in knights:
        await kb.create_knight_directory(knight_id)
        print(f'✓ Initialized {knight_id}')

asyncio.run(init())
"
```

---

## Step 4: Test the Pipeline (1 min)

```python
# Test dispatch with enrichment
python -c "
import asyncio
import sys
sys.path.insert(0, '.')

from control_plane.bifrost import Bifrost

async def test():
    bf = Bifrost()
    
    # First dispatch (establishes baseline)
    print('[1] First dispatch...')
    async for chunk in bf.stream('sir_boris', 'Explain async/await in Python'):
        print(chunk, end='', flush=True)
    print()
    
    # Check tasks.md was updated
    from control_plane.knight_knowledgebase import get_knowledgebase
    kb = get_knowledgebase()
    tasks = await kb.load_tasks('sir_boris')
    print(f'\n✓ Tasks updated: {len(tasks.get(\"completed\", []))} completed')
    
    # Check verification.md
    verification = await kb.load_verification('sir_boris')
    if 'aggregate' in verification:
        print(f'✓ Quality metrics: avg={verification[\"aggregate\"][\"avg_quality\"]}')

asyncio.run(test())
"
```

---

## Step 5: Verify Compression & Search

```python
# Test Qdrant compression
python -c "
import asyncio
from control_plane.symbol_compressor import get_compressor

async def test():
    compressor = get_compressor()
    
    # Get stats for sir_boris
    stats = await compressor.get_knight_stats('sir_boris')
    if stats:
        print(f'✓ Dispatches indexed: {stats[\"total_dispatches\"]}')
        print(f'  Compression ratio: {stats[\"compression_ratio\"]}')
        print(f'  Avg quality: {stats.get(\"success_rate\", 0)}')

asyncio.run(test())
"
```

---

## Step 6: Run Weekly Synthesis (Optional)

```bash
# One-time synthesis run
python -m control_plane.cloudbrain_synthesis
```

Output:
```
[SYNTHESIS] Starting weekly synthesis job...
[SYNTHESIS] Found 47 dispatches from past week
[SYNTHESIS] Clustered into 6 patterns
[SYNTHESIS] Synthesized CODE cluster
[SYNTHESIS] Synthesized RESEARCH cluster
...
[SYNTHESIS] Weekly synthesis job complete
```

---

## Full Test Sequence

```bash
#!/bin/bash
# test_pyramid.sh

echo "=== Knowledge Pyramid Test ==="
echo ""

echo "1. Testing knowledge base..."
python -c "
import asyncio
from control_plane.knight_knowledgebase import get_knowledgebase

async def test():
    kb = get_knowledgebase()
    docs = await kb.load_all('sir_boris')
    print(f'  ✓ Loaded {len(docs)} document sets')

asyncio.run(test())
"

echo ""
echo "2. Testing symbol compression..."
python -c "
import asyncio
from control_plane.symbol_compressor import get_compressor

async def test():
    compressor = get_compressor()
    # Compress sample dispatch
    c = await compressor.compress(
        'test-001', 'sir_boris', 'Test prompt',
        'CODE', 0.9, 20, 100, 234, 'claude-sonnet'
    )
    print(f'  ✓ Compressed dispatch: {c.dispatch_id}')
    
    # Search
    similar = await compressor.find_similar('Similar test', 'sir_boris')
    print(f'  ✓ Found {len(similar)} similar dispatches')

asyncio.run(test())
"

echo ""
echo "3. Testing self-enhancement..."
python -c "
import asyncio
from control_plane.knight_self_enhancer import get_enhancer

async def test():
    enhancer = get_enhancer()
    insights = await enhancer.get_knight_insights('sir_boris')
    if insights.get('aggregate'):
        print(f'  ✓ Enhancement active: {len(insights[\"recent_results\"])} recent')
    else:
        print(f'  ✓ Enhancement ready (no data yet)')

asyncio.run(test())
"

echo ""
echo "=== All systems operational ==="
```

---

## Directory Structure Check

After setup, verify:

```
CAMELOT_OS/
├── 03_VAULT/knights/
│   ├── sir_boris/
│   │   ├── blueprint.md        ← Auto-updated by synthesis
│   │   ├── agent.md
│   │   ├── tasks.md            ← Auto-updated by enhancer
│   │   └── verification.md     ← Auto-updated by enhancer
│   ├── sir_helio/
│   │   ├── blueprint.md
│   │   ├── agent.md
│   │   ├── tasks.md
│   │   └── verification.md
│   └── [10 more knights...]
├── control_plane/
│   ├── knight_knowledgebase.py
│   ├── symbol_compressor.py
│   ├── knight_self_enhancer.py
│   ├── cloudbrain_synthesis.py
│   └── bifrost.py             ← Updated with enrichment
└── KNOWLEDGE_PYRAMID_ARCHITECTURE.md
```

---

## Common Commands

### Check Knight Status

```python
python -c "
import asyncio
from control_plane.knight_knowledgebase import get_knowledgebase
from control_plane.symbol_compressor import get_compressor

async def status():
    kb = get_knowledgebase()
    compressor = get_compressor()
    
    for knight_id in ['sir_boris', 'sir_helio', 'sir_ghost']:
        kb_loaded = await kb.load_all(knight_id)
        stats = await compressor.get_knight_stats(knight_id)
        print(f'{knight_id}:')
        print(f'  Blueprint: {len(kb_loaded[\"blueprint\"])} chars')
        print(f'  Dispatches: {stats.get(\"total_dispatches\", 0)}')
        print(f'  Avg quality: {stats.get(\"success_rate\", 0)}')

asyncio.run(status())
"
```

### View Recent Tasks

```python
python -c "
import asyncio
from control_plane.knight_knowledgebase import get_knowledgebase

async def tasks():
    kb = get_knowledgebase()
    t = await kb.load_tasks('sir_boris')
    for task in t.get('completed', [])[-5:]:
        print(f'  {task[\"prompt\"][:50]}... (quality: {task[\"quality_score\"]})')

asyncio.run(tasks())
"
```

### View Quality Metrics

```python
python -c "
import asyncio
import json
from control_plane.knight_knowledgebase import get_knowledgebase

async def metrics():
    kb = get_knowledgebase()
    v = await kb.load_verification('sir_boris')
    agg = v.get('aggregate', {})
    print(f'Total dispatches: {agg.get(\"total_dispatches\", 0)}')
    print(f'Avg quality: {agg.get(\"avg_quality\", 0)}')
    print(f'Avg latency: {agg.get(\"avg_latency_ms\", 0):.0f}ms')
    print(f'Success rate: {agg.get(\"success_rate\", 0):.0%}')

asyncio.run(metrics())
"
```

---

## Troubleshooting

### Qdrant Not Connected

```bash
# Check if Qdrant is running
curl http://localhost:6333/health
# Should return: {"status":"ok"}

# If not, start Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest
```

### Embedding Model Not Loading

```bash
# Download model manually
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model loaded')
"
```

### Tasks.md Not Updating

```bash
# Check Redis connection
redis-cli ping
# Should return: PONG

# Check permissions on 03_VAULT/knights/
ls -la CAMELOT_OS/03_VAULT/knights/sir_boris/
```

---

## Next: Deploy to Production

Once verified, set up weekly synthesis cron job:

```bash
# Add to crontab
0 23 * * 0 cd /path/to/CAMELOT_OS && python -m control_plane.cloudbrain_synthesis
```

Or use a scheduler:

```python
# control_plane/scheduler.py (future)
import schedule
import asyncio

def weekly_job():
    from control_plane.cloudbrain_synthesis import WeeklySynthesisJob
    job = WeeklySynthesisJob()
    asyncio.run(job.run())

schedule.every().sunday.at("23:00").do(weekly_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Summary

✅ **5 minutes to full pyramid**:
1. Install dependencies
2. Start Qdrant
3. Initialize knight directories
4. Test dispatch pipeline
5. Verify compression

✅ **Knowledge pyramid active**:
- Knowledge base: Load, cache, enrich
- Symbol compression: Dispatch → vector
- Self-enhancement: Learn from work
- Weekly synthesis: Extract patterns

✅ **Knights auto-learn** from each dispatch.
