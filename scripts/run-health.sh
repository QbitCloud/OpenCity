#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
python -m health_pipeline.pipeline
