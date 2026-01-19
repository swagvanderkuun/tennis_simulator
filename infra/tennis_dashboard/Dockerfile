FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
COPY requirements_dashboard.txt /app/requirements_dashboard.txt
RUN pip install --no-cache-dir -r /app/requirements.txt -r /app/requirements_dashboard.txt

# Copy app code
COPY . /app

# Streamlit runtime config via env (defaults exist in compose env file)
CMD ["bash", "-lc", "streamlit run streamlit_dashboard.py --server.address=${DASHBOARD_BIND_IP:-0.0.0.0} --server.port=${DASHBOARD_PORT:-8501} --server.headless=true --browser.gatherUsageStats=false"]





