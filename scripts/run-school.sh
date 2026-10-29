#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
python -m school_pipeline.pipeline
