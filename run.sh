#!/bin/sh
# Starts the macro pad server on the LAN and prints the phone URL.
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt; }
.venv/bin/python -c "import server" >/dev/null
HOST=$(scutil --get LocalHostName).local
TOKEN=$(.venv/bin/python -c "import server; print(server.TOKEN)")
echo "Open on iPhone: http://$HOST:8000/?token=$TOKEN"
exec .venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
