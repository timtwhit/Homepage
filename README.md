# Homepage

A local browser "new tab" / bookmarks dashboard. Drag-to-reorder link tiles,
inline edit mode, a small Python server that persists changes back to disk, and a
click that floats the most-recently-used link toward the top.

## Files

| File | Purpose |
|------|---------|
| `homepage.html` | The dashboard UI. Static; no build step. |
| `links.json` | **Your** link data. Git-ignored (personal URLs). Created on first save. |
| `links.sample.json` | Checked-in example data. Used automatically when `links.json` is absent. |
| `save_server.py` | Local `ThreadingHTTPServer` on port 8765. Serves the static files and handles `POST /save`, which validates the JSON body and writes `links.json`. |
| `open.bat` / `open.vbs` | Launchers. `open.vbs` runs `open.bat` silently; `open.bat` restarts the server and lets it open the tab. |

## Run

```
python save_server.py
```

Then open <http://localhost:8765/homepage.html>. On Windows, double-click
`open.vbs` (or pin `open.bat`) to do both.

## Link data format

```json
{
  "all": [
    { "name": "Google", "url": "https://www.google.com/" },
    { "name": "Wikipedia", "url": "https://en.wikipedia.org/", "favicon": "https://en.wikipedia.org/static/favicon/wikipedia.ico" }
  ],
  "dividerIndex": 1
}
```

- `favicon` is optional; without it the page tries the site's own
  `/favicon.svg`, then `/favicon.ico`, then a DuckDuckGo icon proxy.
- `dividerIndex` is how many links sit above the spacer row.

To seed your own copy: `cp links.sample.json links.json`, then edit in the page.
