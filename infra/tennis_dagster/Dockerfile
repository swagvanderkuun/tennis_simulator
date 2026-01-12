FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps (psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/dagster/app

# Install python deps for the Dagster code location
COPY code_location/requirements.txt /opt/dagster/app/code_location/requirements.txt
RUN pip install --no-cache-dir -r /opt/dagster/app/code_location/requirements.txt

# Copy the code location and install it (so workspace.yaml can load python_package)
COPY code_location/ /opt/dagster/app/code_location/
RUN pip install --no-cache-dir -e /opt/dagster/app/code_location

# Dagster will use this at runtime (mounted by compose)
ENV DAGSTER_HOME=/opt/dagster/dagster_home


