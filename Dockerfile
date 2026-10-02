FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.9.9 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin bot

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src
COPY blocklists ./blocklists
RUN uv sync --frozen --no-dev \
    && mkdir -p /app/data \
    && chown -R bot:bot /app

USER bot

CMD ["uv", "run", "--frozen", "--no-dev", "--no-sync", "safe-bot"]
