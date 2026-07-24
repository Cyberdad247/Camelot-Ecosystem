import asyncio
import time
import os
import sys

# Add 01_KERNEL to sys.path
sys.path.insert(0, os.path.abspath('01_KERNEL/agora/Squires/Memory_Squire'))
sys.path.insert(0, os.path.abspath('01_KERNEL/agora/Squires'))

from open_notebook.domain.notebook import Notebook
from open_notebook.database.repository import repo_query, ensure_record_id

async def create_mock_notebooks(n=10):
    notebook_ids = []
    for i in range(n):
        notebook = Notebook(name=f"Test Notebook {i}", description="Test description")
        await notebook.save()
        notebook_ids.append(notebook.id)
    return notebook_ids

async def run_benchmark(notebook_ids):
    start_time = time.time()

    # Simulate the old N+1 query loop
    for notebook_id in notebook_ids:
        notebook = await Notebook.get(notebook_id)
        if not notebook:
            pass # Handle not found

    end_time = time.time()
    n_plus_one_time = end_time - start_time
    print(f"N+1 approach took: {n_plus_one_time:.4f} seconds for {len(notebook_ids)} notebooks")

    start_time = time.time()

    # Simulate the IN query approach
    # We must ensure IDs are properly formatted for SurrealQL if needed, though $notebook_ids binds them.
    # We'll map them using ensure_record_id to match surreal syntax if they are not already RecordIDs.
    formatted_ids = [ensure_record_id(nid) for nid in notebook_ids]

    query = "SELECT id FROM notebook WHERE id IN $notebook_ids"
    results = await repo_query(query, {"notebook_ids": formatted_ids})
    found_ids = [str(r.get("id")) for r in results] if results else []

    # Check if all specified notebooks exist
    missing_ids = set(notebook_ids) - set(found_ids)
    if missing_ids:
        print(f"Missing some notebooks: {len(missing_ids)}")

    end_time = time.time()
    in_query_time = end_time - start_time
    print(f"IN query approach took: {in_query_time:.4f} seconds for {len(notebook_ids)} notebooks")

    print(f"Improvement: {n_plus_one_time / in_query_time if in_query_time > 0 else 0:.2f}x")

async def main():
    try:
        notebook_ids = await create_mock_notebooks(50)
        await run_benchmark(notebook_ids)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
