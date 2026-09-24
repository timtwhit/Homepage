import http.server
import json
import os
import random
import subprocess
import threading
import traceback
import webbrowser

PORT = 8765
DIR = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(DIR, 'homepage.html')
LINKS_FILE = os.path.join(DIR, 'links.json')
LOG_FILE = os.path.join(DIR, 'server.log')


def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(FILE), **kwargs)

    def do_POST(self):
        log(f'POST {self.path} from {self.client_address} headers={dict(self.headers)}')
        try:
            if self.path == '/save':
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                try:
                    json.loads(body)
                except ValueError as e:
                    log(f'  -> 400 invalid JSON: {e}; body[:200]={body[:200]!r}')
                    self.send_response(400)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'Invalid JSON')
                    return
                with open(LINKS_FILE, 'wb') as f:
                    f.write(body)
                log(f'  -> 200 OK, wrote {len(body)} bytes')
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                log(f'  -> 404 unknown path')
                self.send_response(404)
                self.end_headers()
        except Exception:
            log('  -> EXCEPTION:\n' + traceback.format_exc())
            raise

    def do_OPTIONS(self):
        log(f'OPTIONS {self.path} from {self.client_address}')
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, format, *args):
        pass  # suppress request logs


# Opens a URL through the desktop shell (the running explorer.exe), exactly as
# if the user had clicked it. If Chrome isn't running yet, a Chrome started
# directly by this script (or by `explorer.exe <url>`, which on this Windows
# build just opens Documents) ends up a child of pythonw / the logon scheduled
# task, and that Chrome then silently ignores every link clicked elsewhere
# (Outlook, File Explorer, terminals). Retries while the desktop starts at logon.
DESKTOP_SHELL_OPEN = r'''
$sw = [Activator]::CreateInstance([type]::GetTypeFromCLSID([guid]'9BA05972-F6A8-11CF-A442-00A0C90A8F39'))
for ($i = 0; $i -lt 20; $i++) {
    try {
        $h = 0
        $desk = $sw.FindWindowSW([ref]0, [ref]0, 8, [ref]$h, 1)
        $desk.Document.Application.ShellExecute($args[0])
        exit 0
    } catch { Start-Sleep -Milliseconds 500 }
}
exit 1
'''


def open_browser():
    url = f'http://localhost:{PORT}/homepage.html?_={random.randint(0, 10**9)}'
    if os.name == 'nt':
        try:
            r = subprocess.run(
                ['powershell', '-NoProfile', '-NonInteractive', '-Command',
                 f'& {{{DESKTOP_SHELL_OPEN}}} "{url}"'],
                creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
            if r.returncode == 0:
                return
            log(f'desktop-shell open failed (exit {r.returncode}); falling back')
        except Exception:
            log('desktop-shell open failed; falling back: ' + traceback.format_exc())
    webbrowser.open(url)


with http.server.ThreadingHTTPServer(('', PORT), Handler) as httpd:
    print(f'Serving at http://localhost:{PORT}')
    if os.environ.get('HOMEPAGE_NO_BROWSER') != '1':   # set when a launcher opens the browser itself
        threading.Timer(0.5, open_browser).start()
    httpd.serve_forever()
