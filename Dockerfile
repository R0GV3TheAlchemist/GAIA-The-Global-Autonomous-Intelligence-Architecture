# GAIA Node — Docker Image
# Python 3.11 slim base for production efficiency.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache optimisation)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create data directory for state persistence
RUN mkdir -p /app/data

# Expose the node port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the GAIA node server
CMD ["uvicorn", "node.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
