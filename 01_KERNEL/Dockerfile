# CAMELOT KERNEL [MERLIN_Omega]
# Python 3.13 Slim (matches pyproject.toml requires-python >= 3.13)
FROM python:3.13-slim

# 1. PREP THE FORGE
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MODE=PRODUCTION

# 2. INSTALL SYSTEM DEPENDENCIES
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. CREATE NON-ROOT USER
RUN useradd -m -u 1001 camelot

# 4. INSTALL PYTHON DEPENDENCIES — pinned via uv.lock for reproducible builds
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev

# 5. INSTALL CHROMIUM FOR SIR MASQUE
RUN playwright install chromium && \
    playwright install-deps chromium

# 6. MOUNT THE HIVE
COPY --chown=camelot:camelot . .

# 7. DROP TO NON-ROOT
USER camelot

# 8. EXPOSE PORTS — TitanLink (18788) and API (8000)
EXPOSE 8000 18788

# 9. HEALTH CHECK — polls the /health endpoint every 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 10. LAUNCH THE KERNEL ORCHESTRATOR
CMD ["python", "01_KERNEL/EXCALIBUR/core/excalibur.py"]
