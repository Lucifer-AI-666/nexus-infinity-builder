FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia i file
COPY requirements.txt .
COPY main.py .
COPY api_server.py .
COPY memory.py .
COPY approval_gate.py .
COPY monitoring.py .
COPY task_scheduler.py .

# Installa dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Crea directory per i dati
RUN mkdir -p nexus_memory nexus_approvals nexus_logs

# Espone la porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Avvia l'API server
CMD ["python", "api_server.py"]
