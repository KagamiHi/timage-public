#!/bin/bash
set -euo pipefail

curr_dir="$(dirname "${BASH_SOURCE[0]}")"
cd "${curr_dir}/../"

celery -A backend worker --beat -l debug