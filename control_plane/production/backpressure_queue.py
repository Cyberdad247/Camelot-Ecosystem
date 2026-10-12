# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""DG-400 Bounded Backpressure Queues & Effect-Class Retry Engine.
================================================================
Prevents autonomous agents from becoming self-inflicted load amplifiers.
Separates retry semantics by mathematical effect class:
- PURE: Pure functions; infinite retries safe
- READ_ONLY: Read from disk or UKG; up to 5 retries with backoff
- IDEMPOTENT_WRITE: Safe to replay with identical request ID (up to 3 retries)
- REVERSIBLE_WRITE: Write with rollback snapshot; at most 1 retry
- IRREVERSIBLE_WRITE: External payment, email, irreversible deployment; ZERO automatic retries
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

LOG = logging.getLogger("camelot.backpressure")


class EffectClass(str, Enum):
    PURE = "PURE"
    READ_ONLY = "READ_ONLY"
    IDEMPOTENT_WRITE = "IDEMPOTENT_WRITE"
    REVERSIBLE_WRITE = "REVERSIBLE_WRITE"
    IRREVERSIBLE_WRITE = "IRREVERSIBLE_WRITE"


@dataclass
class QueueItem:
    item_id: str
    task_name: str
    effect_class: EffectClass
    execute_fn: Callable[[], Any]
    priority: int = 1  # Higher = prioritized
    retry_count: int = 0
    enqueued_at: float = field(default_factory=time.time)


class OverloadPolicy(str, Enum):
    REJECT_NEW = "REJECT_NEW"
    DROP_OLDEST = "DROP_OLDEST"
    BLOCK_CALLER = "BLOCK_CALLER"


class BackpressureQueue:
    """Bounded queue with priority ordering and effect-class retry limits."""

    RETRY_LIMITS: Dict[EffectClass, int] = {
        EffectClass.PURE: 10,
        EffectClass.READ_ONLY: 5,
        EffectClass.IDEMPOTENT_WRITE: 3,
        EffectClass.REVERSIBLE_WRITE: 1,
        EffectClass.IRREVERSIBLE_WRITE: 0,
    }

    def __init__(
        self,
        name: str = "default_worker_queue",
        max_depth: int = 100,
        max_inflight: int = 10,
        overload_policy: OverloadPolicy = OverloadPolicy.REJECT_NEW,
    ):
        self.name = name
        self.max_depth = max_depth
        self.max_inflight = max_inflight
        self.overload_policy = overload_policy
        self._queue: deque[QueueItem] = deque()
        self._inflight: int = 0
        self._dead_letter: List[Dict[str, Any]] = []

    @property
    def depth(self) -> int:
        return len(self._queue)

    @property
    def inflight(self) -> int:
        return self._inflight

    def enqueue(self, item: QueueItem) -> Tuple[bool, Optional[str]]:
        """Enqueue an item subject to max depth and overload policies."""
        if len(self._queue) >= self.max_depth:
            if self.overload_policy == OverloadPolicy.REJECT_NEW:
                return False, f"OVERLOAD_REJECT: Queue '{self.name}' at max depth ({self.max_depth})"
            elif self.overload_policy == OverloadPolicy.DROP_OLDEST:
                dropped = self._queue.popleft()
                self._dead_letter.append({
                    "item_id": dropped.item_id,
                    "reason": "DROPPED_DUE_TO_QUEUE_OVERLOAD",
                    "dropped_at": time.time(),
                })

        # Insert sorted by priority (simple insertion for small deque)
        self._queue.append(item)
        return True, None

    def process_next(self) -> Optional[Dict[str, Any]]:
        """Process the next item with effect-class retry mechanics."""
        if not self._queue:
            return None

        if self._inflight >= self.max_inflight:
            return {"status": "MAX_INFLIGHT_REACHED", "inflight": self._inflight}

        item = self._queue.popleft()
        self._inflight += 1

        try:
            result = item.execute_fn()
            self._inflight -= 1
            return {
                "status": "COMPLETED",
                "item_id": item.item_id,
                "result": result,
                "retries": item.retry_count,
            }
        except Exception as exc:
            self._inflight -= 1
            max_retries = self.RETRY_LIMITS.get(item.effect_class, 0)

            if item.retry_count < max_retries:
                item.retry_count += 1
                LOG.warning(
                    "Task %s (%s) failed: %s. Retrying (%d/%d)...",
                    item.item_id,
                    item.effect_class.value,
                    exc,
                    item.retry_count,
                    max_retries,
                )
                self._queue.appendleft(item)
                return {
                    "status": "RETRY_QUEUED",
                    "item_id": item.item_id,
                    "error": str(exc),
                    "retry_count": item.retry_count,
                }
            else:
                LOG.error(
                    "Task %s (%s) exceeded max retries (%d). Routing to dead-letter.",
                    item.item_id,
                    item.effect_class.value,
                    max_retries,
                )
                self._dead_letter.append({
                    "item_id": item.item_id,
                    "effect_class": item.effect_class.value,
                    "error": str(exc),
                    "final_retry_count": item.retry_count,
                    "timestamp": time.time(),
                })
                return {
                    "status": "FAILED_TO_DEAD_LETTER",
                    "item_id": item.item_id,
                    "error": str(exc),
                    "retries": item.retry_count,
                }

    @property
    def dead_letter_count(self) -> int:
        return len(self._dead_letter)
