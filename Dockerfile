# Use slim Python image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies: git (for commits), tzdata, ca-certs
RUN apt-get update && \
    apt-get install -y --no-install-recommends git tzdata ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Workdir inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code folder
COPY Files /app/Files

# Optional: copy GeoLite2 dbs if you want them inside container
# COPY GeoLite2-City.mmdb /app/
# COPY GeoLite2-Country.mmdb /app/

# Git safety
RUN git config --global --add safe.directory /app

# Default envs
ENV MAIN_SCRIPT = Files/app.py

# Entrypoint script to allow looping
RUN printf '%s\n' \
    '#!/bin/sh' \
    'set -e' \
    ': "${MAIN_SCRIPT:=Files/app.py}"' \
    'if [ -n "$GIT_USER_NAME" ]; then git config --global user.name "$GIT_USER_NAME"; fi' \
    'if [ -n "$GIT_USER_EMAIL" ]; then git config --global user.email "$GIT_USER_EMAIL"; fi' \
    'if [ -n "$LOOP_INTERVAL_MINUTES" ]; then' \
    '  echo "Looping every $LOOP_INTERVAL_MINUTES minute(s)";' \
    '  while true; do python "$MAIN_SCRIPT"; sleep $(($LOOP_INTERVAL_MINUTES * 60)); done' \
    'else' \
    '  python "$MAIN_SCRIPT"' \
    'fi' \
    > /usr/local/bin/entry.sh && chmod +x /usr/local/bin/entry.sh

ENTRYPOINT ["/usr/local/bin/entry.sh"]
