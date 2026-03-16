FROM node:20-slim AS frontend
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /usr/src/frontend/

COPY frontend/package.json .
COPY frontend/pnpm-lock.yaml .

RUN --mount=type=cache,id=pnpm,target=${PNPM_HOME}/store \
    pnpm install --frozen-lockfile

ARG EXTERNAL_HOST
ARG VITE_HOST_PREFIX=https
ENV VITE_HOST=${EXTERNAL_HOST}
ENV VITE_HOST_PREFIX=${VITE_HOST_PREFIX}

COPY frontend/ .
RUN pnpm build

FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHON_JIT=1

RUN apt-get update -y && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uv
COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /bin/
ENV UV_LINK_MODE=copy

WORKDIR /usr/src/django_be/

COPY ../pyproject.toml ../uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/usr/src/django_be/.venv/bin:$PATH"

# Backend files
COPY ../backend /usr/src/django_be/backend/
COPY ../users /usr/src/django_be/users/
COPY ../bot /usr/src/django_be/bot/
COPY ../common /usr/src/django_be/common/
COPY ../templates /usr/src/django_be/templates/
COPY ../run /usr/src/django_be/run/
COPY ../name.session /usr/src/django_be/name.session
COPY ../manage.py /usr/src/django_be/manage.py
COPY ../fixtures /usr/src/django_be/fixtures/
# Frontend files
COPY --from=frontend /usr/src/frontend/dist ./frontend/dist
RUN rm -r ./frontend/dist/index.html # using html from template
