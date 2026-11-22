#!/usr/bin/env bash
cd "$(dirname "$0")/.."
source .env

python -m uvicorn SERVER.server:app --port "$API_PORT" &
python -m streamlit run UI/app.py --server.port "$UI_PORT"
