# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port (Railway will provide PORT env var)
EXPOSE ${PORT:-8000}

# Run the FastAPI server
CMD ["sh", "-c", "uv run uvicorn pr_inspector.server_http:app --host 0.0.0.0 --port ${PORT:-8000}"]

