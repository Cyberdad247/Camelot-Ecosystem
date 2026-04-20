# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
[DIRECTIVE QUEUE]
Manages the pending tasks for the Autonomous Swarm.
"""

import json
import os
import shutil
from typing import List, Optional

QUEUE_FILE = "03_VAULT/directives/pending_queue.json"
HISTORY_FILE = "03_VAULT/directives/completed_log.json"

class DirectiveQueue:
    def __init__(self):
        os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
        if not os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "w") as f:
                json.dump([], f)
        
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)

    def push(self, task: str, priority: str = "normal"):
        """Add a task to the queue."""
        with open(QUEUE_FILE, "r") as f:
            queue = json.load(f)
            
        entry = {
            "id": os.urandom(4).hex(),
            "task": task,
            "priority": priority,
            "status": "pending"
        }
        
        # High priority goes to front
        if priority == "high":
            queue.insert(0, entry)
        else:
            queue.append(entry)
            
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)
            
        print(f"📥 [QUEUE] Task Added: {task}")

    def pop(self) -> Optional[dict]:
        """Get the next task."""
        with open(QUEUE_FILE, "r") as f:
            queue = json.load(f)
            
        if not queue:
            return None
            
        task = queue.pop(0)
        task["status"] = "processing"
        
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2)
            
        return task

    def complete(self, task_entry: dict, result: str):
        """Log completion."""
        task_entry["status"] = "completed"
        task_entry["result"] = result
        
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
            
        history.insert(0, task_entry)
        # Keep history manageable (last 100)
        history = history[:100]
        
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
            
        print(f"✅ [QUEUE] Task Completed: {task_entry['task']}")

queue = DirectiveQueue()