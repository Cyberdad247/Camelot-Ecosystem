# Use python 3.12 slim for consistency with Morgana's debian_slim
FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port for local health checks/web service
EXPOSE 8000

# Entrypoint
CMD ["python", "main.py"]
