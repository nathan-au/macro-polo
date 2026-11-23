import hmac
import os
import secrets
import subprocess
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

BASE = Path(__file__).parent
ENV_FILE = BASE / ".env"

app = FastAPI()
MAX_ACTIONS = 8  # the UI is a fixed 2x4 grid


def load_token():
    # Read TOKEN=... from .env; generate and save one if missing or empty.
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == "TOKEN" and value.strip().strip("\"'"):
                return value.strip().strip("\"'")
    t = secrets.token_urlsafe(24)
    with ENV_FILE.open("a") as f:
        f.write(f"TOKEN={t}\n")
    ENV_FILE.chmod(0o600)
    return t


TOKEN = load_token()


def load_actions():
    # Re-read each time so editing actions.yaml needs no restart.
    return yaml.safe_load((BASE / "actions.yaml").read_text()) or []


def authed(request: Request) -> bool:
    supplied = (
        request.headers.get("x-token")
        or request.query_params.get("token")
        or ""
    )
    return hmac.compare_digest(supplied, TOKEN)


@app.middleware("http")
async def require_token(request: Request, call_next):
    if not authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
def index():
    html = (BASE / "static" / "index.html").read_text()
    return html.replace("__TOKEN__", TOKEN)


@app.get("/manifest.json")
def manifest():
    return {
        "name": "Macro Pad",
        "short_name": "Macros",
        "start_url": "/?token=" + TOKEN,
        "display": "standalone",
        "background_color": "#111111",
        "theme_color": "#111111",
        "icons": [],
    }


@app.get("/api/actions")
def list_actions():
    return [
        {
            "id": a["id"],
            "label": a.get("label", a["id"]),
            "icon": a.get("icon", "play.fill"),
        }
        for a in load_actions()[:MAX_ACTIONS]
    ]


@app.post("/run/{action_id}")
def run_action(action_id: str):
    action = next((a for a in load_actions() if a.get("id") == action_id), None)
    if action is None:
        raise HTTPException(404, "unknown action")
    kind = action.get("type")
    try:
        if kind == "shell":
            subprocess.Popen(
                action["command"], shell=True,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, start_new_session=True,
            )
        elif kind == "applescript":
            subprocess.Popen(
                ["osascript", "-e", action["script"]],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, start_new_session=True,
            )
        else:
            raise HTTPException(400, "unknown action type")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, "failed to start: %s" % e)
    return {"status": "started"}
