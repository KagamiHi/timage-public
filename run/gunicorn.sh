#!/bin/bash
set -euo pipefail
dir=$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)

if [ -z "${WEB_CONCURRENCY-}" ];
then
  export WEB_CONCURRENCY=$(($(nproc)))
fi

echo "WEB_CONCURRENCY is '$WEB_CONCURRENCY'";
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py initialize_buckets
#python manage.py loaddata fixtures/*
gunicorn backend.wsgi:application -b 0.0.0.0:8001 --threads 2 --worker-class gthread
