#!/usr/bin/env python3
"""
Signal Board Security Listener
Agents: Network@NHI.com, IT@NHI.com, ITSupport@NHI.com
Runs on every board.json push + daily schedule.
"""

import json, os, sys, hmac, hashlib, base64
from datetime import datetime, timezone, timedelta
from collections import defaultdict

EDT = timezone(timedelta(hours=-4))
EST = timezone(timedelta(hours=-5))

def us_tz():
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

# Security listener aliases — exempt from 1-post/day rule
SECURITY_AGENTS = {"Network@NHI.com", "IT@NHI.com", "ITSupport@NHI.com"}

CROSS_OBEYING_PATTERNS = [
    "lift MT4_PAUSE", "lift pause", "place order", "buy ", "sell ",
    "execute trade", "open position", "close position"
]

MT4_PAUSE_PATTERNS = ["MT4_PAUSE", "lift pause", "resume trading", "unpause"]

def check_sig(msg, secret):
    if "sig" not in msg or not secret:
        return None
    payload = f"{msg.get('ts','')}{msg.get('session','')}{msg.get('msg','')}"
    expected = base64.b64encode(
        hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, msg["sig"])

def date_key(ts_str):
    """Extract YYYY-MM-DD from ISO ts string."""
    try:
        return ts_str[:10]
    except Exception:
        return ts_str

def scan(board_path="board.json"):
    with open(board_path) as f:
        data = json.load(f)

    messages = data.get("messages", [])
    alerts = []
    secret = os.environ.get("BOARD_SECRET", "")

    # 1-post/day tracking: {session: set(dates)}
    posts_per_day = defaultdict(set)

    for m in messages:
        session = m.get("session", "")
        msg_text = m.get("msg", "")
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

        # 3. Cross-obeying
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

        # 5. 1-post/day rule (non-security agents only)
        if session not in SECURITY_AGENTS:
            day = date_key(ts)
            if day in posts_per_day[session]:
                alerts.append({
                    "level": "WARN",
                    "rule": "MULTIPLE_POSTS_PER_DAY",
                    "detail": f"'{session}' posted more than once on {day} (ts={ts})"
                })
            posts_per_day[session].add(day)

    return alerts

def post_alert(alerts, board_path="board.json"):
    if not alerts:
        print(f"[{now_str()}] No issues found.")
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
