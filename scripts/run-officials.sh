#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
exec python -m PIPELINE.officials_pipeline.pipeline
