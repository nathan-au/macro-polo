# Running in the background (macOS)

Instead of keeping a terminal open with `./run.sh`, run the server as a
LaunchAgent. It starts at login, restarts if it crashes, and has no terminal window.

## Setup

1. Make sure the project works once in a terminal first (`./run.sh`). This creates
   `.venv` and `.env` (which holds the token). Stop it with Ctrl+C.
2. Create `~/Library/LaunchAgents/com.nathanau.macro-polo.plist`, replacing `/path/to/macro-polo`
   with the absolute path of your clone and `YOU` with your macOS username:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.nathanau.macro-polo</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/macro-polo/.venv/bin/uvicorn</string>
    <string>server:app</string>
    <string>--host</string><string>0.0.0.0</string>
    <string>--port</string><string>8000</string>
  </array>
  <key>WorkingDirectory</key><string>/path/to/macro-polo</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/Users/YOU/Library/Logs/macro-polo.log</string>
  <key>StandardErrorPath</key><string>/Users/YOU/Library/Logs/macro-polo.log</string>
</dict>
</plist>
```

3. Load it:

```sh
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.nathanau.macro-polo.plist
```

The server is now running. The phone URL is the same as when using `run.sh`:
`http://<LocalHostName>.local:8000/?token=<TOKEN from .env>`. Running `./run.sh`
prints it, but stop the background service first because both use port 8000.

## Managing it

```sh
# Restart (e.g. after editing actions.yaml or server.py)
launchctl kickstart -k gui/$(id -u)/com.nathanau.macro-polo

# Stop and disable
launchctl bootout gui/$(id -u)/com.nathanau.macro-polo

# Start again
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.nathanau.macro-polo.plist

# Check status (first column is the PID, "-" means not running)
launchctl list | grep macro-polo

# Logs
tail -f ~/Library/Logs/macro-polo.log
```

To remove it permanently, run the stop command and delete the plist file.

## Notes

- Use a LaunchAgent (`~/Library/LaunchAgents`), not a LaunchDaemon. Actions need to
  run inside your logged-in GUI session.
- If an action needs macOS permissions (Accessibility, Automation), macOS may prompt
  again because the process is now launched by `uvicorn` rather than your terminal.
  Approve the prompt.
- `bootstrap` fails with an I/O error if the job is already loaded. Run `bootout` first.
