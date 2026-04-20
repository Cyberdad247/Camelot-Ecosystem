# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
from datetime import datetime
from typing import Dict, List, Optional


class Task:
    """Represents a single atomic operation within a plan."""

    def __init__(self, description: str, priority: int = 1):
        self.description = description
        self.priority = priority
        self.status = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
        self.result = None
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "result": self.result,
            "timestamp": self.timestamp,
        }


class Plan:
    """A hierarchical collection of tasks designed to achieve a goal."""

    def __init__(self, goal: str):
        self.goal = goal
        self.tasks: List[Task] = []
        self.current_task_index = 0
        self.created_at = datetime.now().isoformat()
        self.metadata = {}

    def add_task(self, task: Task):
        self.tasks.append(task)

    def next_task(self) -> Optional[Task]:
        if self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    def complete_task(self, result: any):
        if self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index]
            task.status = "COMPLETED"
            task.result = result
            self.current_task_index += 1

    def to_dict(self):
        return {
            "goal": self.goal,
            "tasks": [t.to_dict() for t in self.tasks],
            "current_index": self.current_task_index,
            "created_at": self.created_at,
            "progress": f"{self.current_task_index}/{len(self.tasks)}",
        }


class PlanningEngine:
    """
    🏗️ PLANNING ENGINE: Hierarchical Task Management
    Inspired by Park et al. (2023). Manages the execution stack and plan revision.
    """

    def __init__(self):
        self.active_plans: Dict[str, Plan] = {}

    def create_plan(self, goal: str, subtasks: List[str]) -> str:
        """Initializes a new plan with a set of decomposed tasks."""
        plan_id = f"PLAN_{hash(goal + str(datetime.now())) % 10000}"
        plan = Plan(goal)
        for i, task_desc in enumerate(subtasks):
            plan.add_task(Task(task_desc, priority=i + 1))

        self.active_plans[plan_id] = plan
        return plan_id

    def get_next_action(self, plan_id: str) -> Optional[Dict]:
        """Returns the next task to be executed in a plan."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return None

        task = plan.next_task()
        return task.to_dict() if task else None

    def complete_task(self, plan_id: str, result: any):
        """Marks the current task in a plan as completed."""
        plan = self.active_plans.get(plan_id)
        if plan:
            plan.complete_task(result)

    def revise_plan(self, plan_id: str, feedback: str, new_subtasks: List[str]):
        """
        Dynamically adjusts the plan based on feedback or intermediate observations.
        Essential for 'Architecture of the Heart' autonomy.
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            return

        # Keep completed tasks, but replace/append new ones for the future
        completed = plan.tasks[: plan.current_task_index]
        remaining = [Task(t) for t in new_subtasks]

        plan.tasks = completed + remaining
        plan.metadata["last_revision_feedback"] = feedback

    def export_plan(self, plan_id: str) -> str:
        """Exports the plan state as JSON string."""
        plan = self.active_plans.get(plan_id)
        return json.dumps(plan.to_dict(), indent=2) if plan else "{}"


# Singleton
planner = PlanningEngine()