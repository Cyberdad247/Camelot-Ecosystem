# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from services.celery_tasks import app

worker_options = [
    "worker",
    "--loglevel=INFO",
    "--concurrency=4",
    "--hostname=beifong_worker@%h",
    "--pool=threads",
]

if __name__ == "__main__":
    print("Starting Beifong podcast agent workers...")
    app.worker_main(worker_options)