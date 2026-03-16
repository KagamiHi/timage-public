#!/bin/bash
set -euo pipefail

uv run manage.py migrate
uv run manage.py collectstatic --noinput
uv run manage.py initialize_buckets
uv run manage.py generate_local_images
uv run manage.py runserver 0.0.0.0:8001
