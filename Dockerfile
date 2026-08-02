# syntax=docker/dockerfile:1

FROM python:3.13-slim

WORKDIR /app

# Install system dependencies required by Pillow and for serving static files.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code.
COPY gradio_photo_viewer.py ./
COPY secret-photo-viewer.html ./

# Create the staging directory and a non-root user, then hand ownership over.
# The staging directory is made world-writable with the sticky bit so that a
# runtime volume mount (e.g., docker compose) remains writable for the spv user.
RUN mkdir -p /app/staged_uploads && \
    useradd -m -u 1000 spv && \
    chown -R spv:spv /app && \
    chmod 1777 /app/staged_uploads
USER spv

# The port the app listens on.
EXPOSE 7860

# Health check against the /health endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health').close()" || exit 1

# Run the production server.
CMD ["python", "gradio_photo_viewer.py", "--server_name", "0.0.0.0", "--server_port", "7860"]
