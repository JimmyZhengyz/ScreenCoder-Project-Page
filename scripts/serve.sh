#!/usr/bin/env sh
set -eu

preview_port="${1:-8000}"
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_dir=$(dirname -- "$script_dir")

cd "$project_dir"
exec python3 -m http.server "$preview_port" --bind 127.0.0.1
