#!/bin/bash
set -euo pipefail

docker network inspect traefik-net >/dev/null 2>&1 || docker network create --driver bridge traefik-net
COMPOSE_BAKE=true docker compose \
    -f docker-compose.yaml \
    -f docker-compose.ngrok.yaml \
    up --build "$@"
