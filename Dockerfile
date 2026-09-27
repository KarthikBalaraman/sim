FROM python:3.12-slim

WORKDIR /app

# Ensure logs are emitted immediately (vital for real-time deploy logs)
ENV PYTHONUNBUFFERED=1

# Copy repository files into container
COPY . .

# Default container listening port (Railway injects dynamic PORT at runtime)
EXPOSE 8000

# Start zero-dependency Python server
CMD ["python", "server/server.py"]
