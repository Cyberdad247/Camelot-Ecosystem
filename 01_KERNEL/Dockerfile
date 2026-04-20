# CAMELOT KERNEL [MERLIN_Ω]
# Base: Python 3.11 Slim (Debian)
FROM python:3.11-slim

# 1. PREP THE FORGE
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. INSTALL SYSTEM DEPENDENCIES (For Kinetic Tools)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. INSTALL PYTHON DEPENDENCIES
# Core: FastAPI, Uvicorn, Requests
# Kinetic: Playwright, Psutil, Numpy (Physics)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. INSTALL BROWSERS (For Sir Masque)
RUN playwright install chromium
RUN playwright install-deps

# 5. MOUNT THE HIVE
# We copy the source code, but the .hive memory will be a volume
COPY . .

# 6. ACTIVATE MERLIN
# Expose TitanLink (18788) and API (8000)
EXPOSE 8000 18788

# Default Command: Launch the Kernel Orchestrator
CMD ["python", "core/excalibur.py"]