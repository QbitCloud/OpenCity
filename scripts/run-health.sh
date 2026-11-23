#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
exec python -m PIPELINE.health_pipeline.pipeline
