#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
source .venv/bin/activate
source .env

# Check that an older server is not already running.
for port in "$API_PORT" "$UI_PORT"; do
    if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
        echo "Port $port is already in use. Stop the old server first."
        exit 1
    fi
done

mkdir -p data/logs

# Backend and UI.
python -m uvicorn SERVER.server:app --port "$API_PORT" &
backend_pid=$!

python -m streamlit run UI/app.py --server.port "$UI_PORT" &
ui_pid=$!

# Run the existing pipeline scripts one at a time.
run_pipeline() {
    bash "$1" &
    current_pipeline_pid=$!
    wait "$current_pipeline_pid" || echo "Pipeline failed: $1"
}

# Refresh in the background only on the 1st of each month.
(
    current_pipeline_pid=""
    trap 'kill "$current_pipeline_pid" 2>/dev/null || true; exit 0' INT TERM
    last_month=""

    while true; do
        day=$(TZ=Asia/Kolkata date +%d)
        month=$(TZ=Asia/Kolkata date +%Y-%m)

        if [ "$day" = "01" ] && [ "$month" != "$last_month" ]; then
            echo "Pipeline refresh: $(date)"

            run_pipeline SCRIPTS/run-school.sh
            run_pipeline SCRIPTS/run-health.sh
            run_pipeline SCRIPTS/run-hospital.sh
            run_pipeline SCRIPTS/run-court.sh
            run_pipeline SCRIPTS/run-officials.sh
            run_pipeline SCRIPTS/run-water-and-finance.sh

            last_month=$month
            echo "Refresh finished."
        fi

        sleep 60 &
        current_pipeline_pid=$!
        wait "$current_pipeline_pid"
    done
) >> data/logs/pipelines.log 2>&1 &
pipeline_pid=$!

# Stop everything when Ctrl+C is pressed.
cleanup() {
    kill "$backend_pid" "$ui_pid" "$pipeline_pid" 2>/dev/null || true
    wait "$backend_pid" "$ui_pid" "$pipeline_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 0' INT TERM

printf 'Dashboard: http://localhost:%s\n' "$UI_PORT"
echo "Pipeline logs: data/logs/pipelines.log"

while kill -0 "$backend_pid" 2>/dev/null && kill -0 "$ui_pid" 2>/dev/null; do
    sleep 2
done

echo "Backend or UI stopped. Closing the system."
exit 1
