FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# install what you actually need
RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      ca-certificates \
      cron \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy your code
COPY Files/ /app/Files/

# safe git dir if update_git.py is used
RUN git config --global --add safe.directory /app/Files

# create cron log
RUN touch /var/log/cron.log

# write crontab (every 2h, cd into /app/Files, run app.py)
# IMPORTANT: must end with a newline
RUN echo "0 */2 * * * cd /app/Files && github_token=\$github_token /usr/local/bin/python -u app.py >> /var/log/cron.log 2>&1" \
    > /etc/cron.d/app-cron \
 && chmod 0644 /etc/cron.d/app-cron \
 && crontab /etc/cron.d/app-cron

# start: run once immediately, then cron in foreground, and tail logs
CMD cd /app/Files && python -u app.py >> /var/log/cron.log 2>&1 || true; \
    cron -f & \
    tail -F /var/log/cron.log
