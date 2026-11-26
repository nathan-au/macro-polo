# Agent instructions

The server runs in the background as a LaunchAgent (see `BACKGROUND.md`).

After every change to the project (`server.py`, `actions.yaml`, `static/`, or anything else
the server loads), restart the service so the change takes effect:

```sh
launchctl kickstart -k gui/$(id -u)/com.nathanau.macro-polo
```

Then check that it came back up (the first column should be a PID, not `-`):

```sh
launchctl list | grep macro-polo
```

If it isn't running, check `~/Library/Logs/macro-polo.log`.
