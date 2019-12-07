# Build stage
FROM python:3

RUN groupadd -g 500 taalbot && \
    useradd -d /home/taalbot -g taalbot -m -N -u 500 taalbot

USER taalbot

RUN python3 -m venv /home/taalbot/venv
COPY requirements.txt .

ENV PATH "/home/taalbot/venv/bin:$PATH"
RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3-slim

RUN groupadd -g 500 taalbot && \
    useradd -d /home/taalbot -g taalbot -m -N -u 500 taalbot && \
    mkdir -p /srv/taalbot && \
    chown taalbot:taalbot /srv/taalbot

USER taalbot
WORKDIR /srv/taalbot

COPY --chown=taalbot:taalbot . .
COPY --chown=taalbot:taalbot run.sh /
COPY --from=0 /home/taalbot/venv /home/taalbot/venv

ENV PATH="/home/taalbot/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/home/taalbot/venv

CMD ["/run.sh"]
