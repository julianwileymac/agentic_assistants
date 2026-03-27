#!/bin/sh
# Seed Dagster instance config when DAGSTER_HOME is an empty Docker volume.
# Without this, COPY'd dagster.yaml / workspace.yaml from the image are hidden.

set -e

DAGSTER_HOME="${DAGSTER_HOME:-/opt/dagster/dagster_home}"
TEMPLATE_DIR="${DAGSTER_TEMPLATE_DIR:-/opt/dagster/dagster_config_templates}"

mkdir -p "$DAGSTER_HOME/compute_logs" "$DAGSTER_HOME/artifacts"

if [ ! -f "$DAGSTER_HOME/dagster.yaml" ] && [ -f "$TEMPLATE_DIR/dagster.yaml" ]; then
  echo "dagster-entrypoint: seeding dagster.yaml into $DAGSTER_HOME"
  cp "$TEMPLATE_DIR/dagster.yaml" "$DAGSTER_HOME/dagster.yaml"
fi

if [ ! -f "$DAGSTER_HOME/workspace.yaml" ] && [ -f "$TEMPLATE_DIR/workspace.yaml" ]; then
  echo "dagster-entrypoint: seeding workspace.yaml into $DAGSTER_HOME"
  cp "$TEMPLATE_DIR/workspace.yaml" "$DAGSTER_HOME/workspace.yaml"
fi

exec "$@"
