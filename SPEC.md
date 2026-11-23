# Phone Macro Pad: Spec

## Goal
Turn an iPhone into a button pad that triggers actions on a MacBook (shell commands, AppleScript). Local-first, free, no external hosting.

## Architecture
- **Server (Mac):** small Python FastAPI app. Serves the web UI and exposes an API to run actions.
- **Client (iPhone):** web page (PWA) saved to the Home Screen via Safari. Shows a grid of buttons.
- **Flow:** tap button -> `POST /run/{action_id}` -> server starts the action -> returns only a "started" confirmation (or an error if it failed to start) -> phone shows a brief "Started" toast. No command output is sent back.
- **Network:** phone and Mac are always on the same Wi-Fi network. The phone connects via the Mac's LAN address (e.g. `http://<mac>.local:8000`). No Tailscale or remote access.

## Config
Actions are defined in one file (`actions.yaml`). Editing it changes the buttons; no code changes needed.

```yaml
- id: open_s27_apps
  label: S27 apps
  icon: "📊"
  type: shell
  command: 'open -a "Microsoft Excel" "/Users/nathanau/Workspace/s27-apps.xlsx"'
- id: stage_list_new
  label: Stage list (new)
  icon: "🖥️"
  type: applescript
  script: |
    tell application "Terminal"
      activate
      do script "cd ~/Workspace && stage list --new --all"
    end tell
```

## Action types
| Type | Does |
|------|------|
| `shell` | Runs a predefined command |
| `applescript` | Runs a predefined AppleScript (open apps, drive Terminal, etc.) |

## MVP scope
1. FastAPI server with `/` (UI), `/api/actions` (list), `/run/{id}` (execute).
2. Responsive button-grid UI, installable to Home Screen. Tapping a button runs it immediately (no confirmation) and shows a "Started" toast.
3. Config-driven actions from `actions.yaml`.
4. Single page of buttons.
5. Shared-secret token on requests.

## Starter actions
1. **S27 apps:** opens `/Users/nathanau/Workspace/s27-apps.xlsx` in Microsoft Excel.
2. **Stage list (new):** opens a Terminal window, runs `stage list --new --all` from `~/Workspace`. Uses Terminal (not the server's own shell) so the user's login PATH is available for the `stage` command.

## Security
- Only actions defined in `actions.yaml` can run; the phone never sends raw commands.
- Shared secret token required on every request.
- Bind to the local network only; no public exposure.

## Requirements
- Mac with Python 3 and `fastapi`, `uvicorn`, `pyyaml` (no specific Python version pinned).
- iPhone with Safari on the same Wi-Fi network as the Mac.
- Mac must be on, awake, and the server started manually (`uvicorn ...`).

## Out of scope (v1)
- Native iOS app, haptics, lock-screen widgets.
- Launch at login.
- Confirmation prompts on the phone.
- Returning command output to the phone.
- Remote/away-from-home access (Tailscale).
- Claude API actions.
- Multiple pages or folders of buttons.

## Future ideas
- More starter buttons.
- `claude` action type (needs API key, uses credits).
- Auto-start at login via `launchd`.