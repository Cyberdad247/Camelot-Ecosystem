#!/usr/bin/env python3
"""Verify all knight roster has cloud brains, including KBA services node.
Queries the active NotebookLM list and creates any missing brain instances.
"""
import asyncio
import os
import sys

# Add configs to path for notebooklm_bridge
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "03_VAULT", "training", "configs")))

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    from notebooklm import NotebookLMClient
    from notebooklm.auth import AuthTokens, fetch_tokens, load_auth_from_storage
    
    print("Connecting to NotebookLM...")
    try:
        cookies = load_auth_from_storage()
        csrf, session = await fetch_tokens(cookies)
        tokens = AuthTokens(cookies=cookies, csrf_token=csrf, session_id=session)
        
        async with NotebookLMClient(auth=tokens) as client:
            print("Fetching active notebooks list...")
            notebooks = await client.notebooks.list()
            
            existing_titles = {nb.title: nb.id for nb in notebooks}
            print(f"Discovered {len(notebooks)} existing notebooks in CloudBrain:")
            for title, nb_id in existing_titles.items():
                print(f"  - '{title}' (ID: {nb_id})")
                
            # Check target notebooks
            required_notebooks = [
                "The Heimdall UKG Nano Sovereign",
                "CAMELOT-OS: Sir Heimdall (The Bifrost Guardian)",
                "Merlin: AI Mythosmith",
                "Ancestral Chimera Research Swarm",
                "Pydantic AI",
                "Camelot-OS v.999.3",
                "Kickbox Audio (KBA) Services Node"  # The KBA services node brain
            ]
            
            print("\nVerifying targets...")
            for target in required_notebooks:
                if target in existing_titles:
                    print(f"  [OK]  '{target}' is active (ID: {existing_titles[target]})")
                else:
                    print(f"  [ADD] '{target}' not found. Spawning new CloudBrain...")
                    try:
                        nb = await client.notebooks.create(title=target)
                        print(f"        Created successfully! ID: {nb.id}")
                        existing_titles[target] = nb.id
                    except Exception as spawn_err:
                        print(f"        Failed to create '{target}': {spawn_err}")
                        
            print("\n--- CLOUDBRAIN VERIFICATION COMPLETE ---")
            
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
