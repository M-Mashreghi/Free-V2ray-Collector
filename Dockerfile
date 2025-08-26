FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        tzdata \
        ca-certificates \
        curl \
        cron \
        nano \
    && rm -rf /var/lib/apt/lists/*

# Workdir inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code folder
COPY Files /app/Files

# Set working directory to Files folder
WORKDIR /app/Files

# Git safety
RUN git config --global --add safe.directory /app/Files

# Define default script
ENV MAIN_SCRIPT=app.py

# Create cron job to run every 2 hours
RUN echo "0 */2 * * * root cd /app/Files && /usr/local/bin/python $MAIN_SCRIPT >> /var/log/cron.log 2>&1" > /etc/cron.d/mycron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/mycron && \
    crontab /etc/cron.d/mycron

# Create the log file
RUN touch /var/log/cron.log

# Install cron and start it in foreground mode
RUN chmod +x $MAIN_SCRIPT

# Run the script immediately when container starts and then every 2 hours
CMD echo "Starting initial run..." && \
    cd /app/Files && python $MAIN_SCRIPT >> /var/log/cron.log 2>&1 && \
    echo "Starting cron service..." && \
    cron && \
    echo "Container started. Script will run every 2 hours." && \
    tail -f /var/log/cron.log
