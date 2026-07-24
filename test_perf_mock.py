import asyncio
import time

async def get_notebook_mock(notebook_id):
    await asyncio.sleep(0.01) # Simulate DB lookup
    return {"id": notebook_id, "name": f"Notebook {notebook_id}"}

async def get_notebooks_in_query_mock(notebook_ids):
    await asyncio.sleep(0.015) # Simulate DB lookup, slightly slower for IN query but not N times slower
    return [{"id": nid} for nid in notebook_ids]

async def run_benchmark(notebook_ids):
    start_time = time.time()

    # Simulate the old N+1 query loop
    for notebook_id in notebook_ids:
        notebook = await get_notebook_mock(notebook_id)
        if not notebook:
            pass # Handle not found

    end_time = time.time()
    n_plus_one_time = end_time - start_time
    print(f"N+1 approach took: {n_plus_one_time:.4f} seconds for {len(notebook_ids)} notebooks")

    start_time = time.time()

    # Simulate the IN query approach
    results = await get_notebooks_in_query_mock(notebook_ids)
    found_ids = [r.get("id") for r in results]

    # Check if all specified notebooks exist
    missing_ids = set(notebook_ids) - set(found_ids)
    if missing_ids:
        print(f"Missing some notebooks: {len(missing_ids)}")

    end_time = time.time()
    in_query_time = end_time - start_time
    print(f"IN query approach took: {in_query_time:.4f} seconds for {len(notebook_ids)} notebooks")

    print(f"Improvement: {n_plus_one_time / in_query_time if in_query_time > 0 else 0:.2f}x")

async def main():
    notebook_ids = [f"test:{i}" for i in range(50)]
    await run_benchmark(notebook_ids)

if __name__ == "__main__":
    asyncio.run(main())
