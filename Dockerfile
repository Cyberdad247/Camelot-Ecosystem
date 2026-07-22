FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml package.json ./

RUN apt-get update && apt-get install -y curl gcc
RUN pip install uv
RUN uv pip install -r pyproject.toml || true

COPY . .

CMD ["python", "-m", "control_plane.hive_boot", "--no-tui"]
