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


# Add crontab file (run every 2 hours)
# Note: Use absolute path for python and script
RUN echo "0 */2 * * * cd /app/Files && /usr/local/bin/python3 $MAIN_SCRIPT >> /var/log/cron.log 2>&1" > /etc/cron.d/mycron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/mycron && \
    crontab /etc/cron.d/mycron

# Create the log file
RUN touch /var/log/cron.log

# Start cron and keep container running
CMD cron && tail -f /var/log/cron.log
