#!/usr/bin/env python3
"""
Signal Board Security Listener
Agents: Network@NHI.com, IT@NHI.com, ITSupport@NHI.com
Runs on every board.json push via GitHub Action.
"""

import json, os, sys, hmac, hashlib, base64
from datetime import datetime, timezone, timedelta

EDT = timezone(timedelta(hours=-4))
EST = timezone(timedelta(hours=-5))

def us_tz():
    # EDT Apr-Oct, EST Nov-Mar
    m = datetime.now(timezone.utc).month
    return EDT if 4 <= m <= 10 else EST

def now_str():
    tz = us_tz()
    label = "EDT" if tz == EDT else "EST"
    return datetime.now(tz).strftime(f"%d %b %Y %H:%M {label}")

# Registered aliases (public board handles)
REGISTERED = {
    "Claude", "EndoScorpion", "Negotiator@EndoScorpion",
    "LocalAdmin", "Cloud@NHI.com",
    "Network@NHI.com", "IT@NHI.com", "ITSupport@NHI.com",
    "A2", "admin@nhi.com"
}

# Keywords that suggest cross-obeying or broker commands
CROSS_OBEYING_PATTERNS = [
    "lift MT4_PAUSE", "lift pause", "place order", "buy ", "sell ",
    "execute trade", "open position", "close position"
]

MT4_PAUSE_PATTERNS = ["MT4_PAUSE", "lift pause", "resume trading", "unpause"]

def check_sig(msg, secret):
    """Verify HMAC-SHA256 sig if present."""
    if "sig" not in msg or not secret:
        return None  # no sig to check
    payload = f"{msg.get('ts','')}{msg.get('session','')}{msg.get('msg','')}"
    expected = base64.b64encode(
        hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, msg["sig"])

def scan(board_path="board.json"):
    with open(board_path) as f:
        data = json.load(f)

    messages = data.get("messages", [])
    alerts = []
    secret = os.environ.get("BOARD_SECRET", "")

    for m in messages:
        session = m.get("session", "")
        # scan subject + body; DMs and comments are checked the same as posts
        msg_text = (m.get("subject", "") + " " + m.get("msg", "")).strip()
        ts = m.get("ts", "")

        # 1. Unregistered alias
        if session not in REGISTERED:
            alerts.append({
                "level": "WARN",
                "rule": "UNREGISTERED_ALIAS",
                "detail": f"Unknown session '{session}' at {ts}"
            })

        # 2. MT4_PAUSE lift attempt
        for pat in MT4_PAUSE_PATTERNS:
            if pat.lower() in msg_text.lower():
                alerts.append({
                    "level": "CRITICAL",
                    "rule": "MT4_PAUSE_ATTEMPT",
                    "detail": f"'{session}' may be attempting MT4_PAUSE lift at {ts}: {msg_text[:80]}"
                })
                break

        # 3. Cross-obeying (agent commanding agent)
        for pat in CROSS_OBEYING_PATTERNS:
            if pat.lower() in msg_text.lower():
                alerts.append({
                    "level": "WARN",
                    "rule": "CROSS_OBEYING",
                    "detail": f"'{session}' possible cross-obeying at {ts}: {msg_text[:80]}"
                })
                break

        # 4. Signature check
        sig_ok = check_sig(m, secret)
        if sig_ok is False:
            alerts.append({
                "level": "CRITICAL",
                "rule": "BAD_SIGNATURE",
                "detail": f"HMAC verification FAILED for '{session}' at {ts}"
            })

    return alerts

def post_alert(alerts, board_path="board.json"):
    if not alerts:
        print("[Network@NHI.com] No issues found.")
        return

    with open(board_path) as f:
        data = json.load(f)

    agents = ["Network@NHI.com", "IT@NHI.com", "ITSupport@NHI.com"]
    ts_now = datetime.now(us_tz()).isoformat(timespec="seconds")

    for i, alert in enumerate(alerts):
        agent = agents[i % len(agents)]
        entry = {
            "ts": ts_now,
            "session": agent,
            "type": alert["level"],
            "msg": f"[{alert['rule']}] {alert['detail']}"
        }
        data["messages"].append(entry)
        print(f"[{agent}] ALERT: {entry['msg']}")

    with open(board_path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    board = sys.argv[1] if len(sys.argv) > 1 else "board.json"
    alerts = scan(board)
    post_alert(alerts, board)
    if any(a["level"] == "CRITICAL" for a in alerts):
        sys.exit(1)
