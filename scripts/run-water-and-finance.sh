#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
python3 -m PIPELINE.water_and_finance_pipeline.pipeline
python3 -m PIPELINE.water_and_finance_pipeline.pipeline --water-from-year 2024
