#!/usr/bin/env bash
# Linux/WSL launcher - same job as open.bat: (re)start the server on 8765 and open the page.
#
# With systemd available the server runs as a user unit so it outlives the `wsl.exe`
# session that launched it. A systemd service cannot start Windows programs (no WSL
# interop), so the unit runs with HOMEPAGE_NO_BROWSER=1 and this script - which runs in
# a real WSL session - opens the browser itself once the port answers.
cd "$(dirname "$(readlink -f "$0")")" || exit 1
url="http://localhost:8765/homepage.html?_=$RANDOM$RANDOM"

log="$HOME/homepage-open.log"
open_url() {
  if grep -qi microsoft /proc/version; then
    /mnt/c/Windows/System32/rundll32.exe url.dll,FileProtocolHandler "$url"
    echo "$(date -Is) opened $url rc=$? interop=${WSL_INTEROP:-none}" >> "$log"
  else
    xdg-open "$url" >/dev/null 2>&1 || true
  fi
}
wait_port() { for _ in $(seq 1 30); do (echo >/dev/tcp/127.0.0.1/8765) 2>/dev/null && return 0; sleep 0.2; done; return 1; }

if systemctl --user cat homepage.service >/dev/null 2>&1; then
  systemctl --user restart homepage.service
  echo "$(date -Is) restart rc=$?" >> "$log"
  if wait_port; then open_url; else echo "$(date -Is) port 8765 never answered" >> "$log"; fi
  exit 0
fi

# No installed unit: transient unit if systemd is around, plain background job otherwise.
systemctl --user stop homepage.service 2>/dev/null
fuser -k 8765/tcp >/dev/null 2>&1
sleep 1
if command -v systemd-run >/dev/null && systemctl --user is-system-running >/dev/null 2>&1; then
  systemd-run --user --quiet --unit=homepage --working-directory="$PWD" \
    --setenv=HOMEPAGE_NO_BROWSER=1 python3 save_server.py
  wait_port && open_url
else
  nohup setsid python3 save_server.py >/dev/null 2>&1 &
fi
