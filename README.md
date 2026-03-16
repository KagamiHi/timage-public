# timage

A Telegram-based image swipe platform built with Django, Svelte, and Celery.

## Stack

- **Backend**: Django 5, Django REST Framework, Celery
- **Frontend**: Svelte 5, TypeScript, Tailwind CSS, Vite
- **Database**: PostgreSQL 17
- **Cache / Broker**: Redis
- **Storage**: MinIO (S3-compatible)
- **Bot**: aiogram + telethon (Telegram)
- **Catcher**: Telegram image scraper service _(WIP — not yet production-ready)_
- **Proxy**: Traefik

## Project structure

```
backend/        Django project settings
bot/            Telegram bot, image models, swipe API
common/         Shared models, middleware, utilities
frontend/       Svelte SPA (Telegram Mini App)
users/          User model and Telegram auth
dockerfiles/    Dockerfiles for all services
fixtures/       Local development fixtures
run/            Gunicorn / Celery entrypoint scripts
templates/      Django HTML templates
```

## Local development

### Prerequisites

- Docker & Docker Compose
- Telegram bot token and API credentials

### Setup

1. Copy the environment template and fill in your values:

   ```bash
   cp .env.example .env
   ```

   Required credentials:
   - **Telegram API**: get `API_ID` and `API_HASH` at <https://my.telegram.org/apps>
   - **Bot token**: create a bot via [@BotFather](https://t.me/BotFather) to get `BOT_TOKEN`

2. Run tests (SQLite in-memory, no external services needed):

   ```bash
   uv run manage.py test
   ```

3. Start all services:

   ```bash
   ./up.sh
   ```

   This command builds the images and starts the full stack with local overrides (Django dev server, fixture user, 5 placeholder images, no catcher).

   On first run the following happens automatically:
   - Database migrations
   - MinIO bucket initialization
   - Fixture user loaded (`tlg_id=1`, superuser)
   - 5 placeholder images generated for swiping

4. Open <http://localhost:8001> in your browser.

> **Note:** `up.sh` uses `docker-compose.local.yaml` overrides — it is intended for local use only, not production.

### Local auth

In local mode (`LOCAL=1`) authentication is bypassed: every request is authenticated as the fixture user and `/api/tlg-token/` returns a JWT token without Telegram WebApp validation.

### Bot polling

Set `TLG_LONG_POLLING=1` in `.env` to use long polling instead of webhooks (no ngrok needed locally).

## Internet-accessible local deployment (ngrok)

Use this when you need real Telegram auth — for example, to test the Mini App from your phone. Unlike `up.sh`, this mode does **not** bypass authentication.

Traefik runs as part of the stack and routes traffic:
- `/cdn/*` → MinIO
- `/bot/*` → Telegram bot webhook
- `/*` → Django

ngrok tunnels port 80 to a public HTTPS URL set as `EXTERNAL_HOST`, baked into the frontend build.

### Prerequisites

- ngrok installed and configured ([get started](https://dashboard.ngrok.com/get-started/setup/linux))
- All credentials filled in `.env`
- `EXTERNAL_HOST` set in `.env` to your ngrok static domain — get one free at [dashboard.ngrok.com/domains](https://dashboard.ngrok.com/domains)

### Setup

1. In [@BotFather](https://t.me/BotFather): set the Menu Button URL to `https://<your-ngrok-domain>/`.

2. Start ngrok tunnel (run in a separate terminal):

   ```bash
   ngrok http --url="$EXTERNAL_HOST" 80
   ```

3. Deploy the stack:

   ```bash
   ./up-ngrok.sh
   ```

   Builds the image with the correct `EXTERNAL_HOST` and starts all services including Traefik.

> **Note:** ngrok must be running before requests reach the stack. Keep the ngrok terminal open.

## Production deployment

The project uses Docker Swarm with Traefik for TLS termination.

1. Set up a server with Docker Swarm initialized.
2. Fill `.env` with production values (`EXTERNAL_HOST`, etc.).
3. Deploy:

   ```bash
   docker stack deploy -c docker-compose.yaml -c docker-compose.traefik.yaml timage
   ```

## Environment variables

See [.env.example](.env.example) for a full list of required variables.
