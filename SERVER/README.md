# OpenCity backend

The backend uses FastAPI and Uvicorn.

## Setup on macOS/Linux

Run these commands from the repository root:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r SERVER/requirments.txt
    python -m uvicorn SERVER.server:app --reload

The dependency filename is currently spelled requirments.txt.

Open http://127.0.0.1:8000/docs to try the API.

## Endpoints

- GET / returns a Hello World message.
- GET /hello/{name} returns a greeting for the supplied name.

Press Control+C in Terminal to stop the server.

## Verification

Started locally with Python 3.9.6.
Confirmed that GET / returns the expected greeting.
Ran pip check: no broken requirements found.
