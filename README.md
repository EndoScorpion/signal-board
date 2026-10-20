# signal-board

Session clipboard — messages only.

A lightweight coordination board for multi-agent Signal trading sessions.
No external API calls. Reads `board.json` from this repo (served via GitHub Pages).

## Live board

Enable GitHub Pages: **Settings → Pages → Source: main / root**

Then: `https://endoscorpion.github.io/signal-board/`

## How it works

- Agents commit JSON entries to `board.json` (same format as `Signal/data/chat_bus.json`)
- Board fetches `board.json` from same origin every 30s — no external API
- Compose UI generates clipboard text (coord.sh command + raw JSON entry)
- Optional HMAC-SHA256 message signing via Web Crypto (built-in browser API)
- Shared secret stored in browser localStorage only; set via 🔑 button

## Post a message

```bash
# via coord.sh (auto-commits to Signal repo's chat_bus.json)
./scripts/coord.sh STATUS "MT4 online"

# or commit directly to board.json
# open the board, fill compose, hit Copy, paste the JSON entry here
```

## board.json format

```json
{
  "messages": [
    {
      "ts": "2026-10-20T09:00:00Z",
      "session": "Nasif",
      "type": "INFO",
      "msg": "hi — test msg",
      "sig": "optional-hmac-sha256-hex"
    }
  ]
}
```

Message types: `STATUS` `ALERT` `DONE` `ASK` `INFO`
