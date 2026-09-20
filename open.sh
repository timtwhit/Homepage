#!/usr/bin/env bash
# Linux/WSL launcher - same job as open.bat: (re)start the server on 8765, and it
# opens the browser itself. Under WSL there is no Linux browser, so BROWSER points
# Python's webbrowser module at Windows' default browser.
#
# With systemd available the server runs as a user unit so it outlives the
# `wsl.exe` session that launched it (plain nohup children are killed when that
# session ends). An installed homepage.service (see the dev-setup repo's
# systemd/ folder) is preferred; otherwise a transient unit is used.
cd "$(dirname "$(readlink -f "$0")")" || exit 1

if grep -qi microsoft /proc/version; then
  export BROWSER='/mnt/c/Windows/System32/rundll32.exe url.dll,FileProtocolHandler %s'
fi

if systemctl --user cat homepage.service >/dev/null 2>&1; then
  exec systemctl --user restart homepage.service
fi

systemctl --user stop homepage.service 2>/dev/null
fuser -k 8765/tcp >/dev/null 2>&1
sleep 1
if command -v systemd-run >/dev/null && systemctl --user is-system-running >/dev/null 2>&1; then
  systemd-run --user --quiet --unit=homepage --working-directory="$PWD" \
    ${BROWSER:+--setenv=BROWSER="$BROWSER"} python3 save_server.py
else
  nohup setsid python3 save_server.py >/dev/null 2>&1 &
fi
