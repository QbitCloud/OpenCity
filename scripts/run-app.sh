#!/usr/bin/env bash
cd "$(dirname "$0")/.."

python -m uvicorn SERVER.server:app --port 8000 &
python -m streamlit run UI/app.py --server.port 8501
