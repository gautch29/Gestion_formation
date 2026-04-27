#!/bin/sh
set -eu

: "${DATABASE_PATH:=/app/data/bdd_formations.db}"

database_dir="$(dirname "$DATABASE_PATH")"
mkdir -p "$database_dir"

if [ ! -f "$DATABASE_PATH" ] && [ -f /app/bdd_formations.db ]; then
  cp /app/bdd_formations.db "$DATABASE_PATH"
fi

exec "$@"
