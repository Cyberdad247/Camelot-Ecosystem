import json

def read_queue_stats():
    """Read harness_queue.jsonl and return a dict with total, pending, and done counts."""
    with open('harness_queue.jsonl', 'r') as f:
        stats = {}
        for line in f:
            line = line.strip()
            if 'total' in line:
                stats['total'] = stats.get('total', 0) + 1
            if 'pending' in line:
                stats['pending'] = stats.get('pending', 0) + 1
            if 'done' in line:
                stats['done'] = stats.get('done', 0) + 1
    return stats
