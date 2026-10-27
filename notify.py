#!/usr/bin/env python3
"""
Signal Board thread notifications.

Compares board.json before/after a push and works out who should hear about
each new reply, comment, edit or DM: thread followers (board.json
"subscriptions"), tagged handles (@handle or "to"), and the DM recipient.
The author never gets their own notification, and admin-hidden posts are skipped.

Emails link back to the thread: <BOARD_URL>inbox.html#t=<root ts>&m=<msg ts>

Handle -> email lives in the NOTIFY_CONTACTS secret (JSON object), never in
the public board. Sending is OFF unless NOTIFY_SEND=1 and SMTP_* secrets are
set; otherwise this is a dry run that only prints handles (no addresses),
since Actions logs on a public repo are public.

Usage: python3 notify.py OLD_BOARD.json NEW_BOARD.json
"""

import json, os, sys, smtplib, ssl
from email.message import EmailMessage
from urllib.parse import quote

BOARD_URL = (os.environ.get("BOARD_URL") or "https://endoscorpion.github.io/signal-board/").rstrip("/") + "/"


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"messages": []}


def root_of(m, by_ts):
    seen = 0
    while m.get("reply_to") in by_ts and seen < 100:
        m = by_ts[m["reply_to"]]
        seen += 1
    return m


def tags_of(m, handles):
    out = set(m.get("to") or [])
    body = m.get("msg", "")
    for h in handles:
        if "@" + h in body:
            out.add(h)
    return out


def thread_link(root_ts, msg_ts=None):
    url = f"{BOARD_URL}inbox.html#t={quote(root_ts, safe='')}"
    if msg_ts and msg_ts != root_ts:
        url += f"&m={quote(msg_ts, safe='')}"
    return url


def changes(old, new):
    """Yield (event, message) for messages that are new or edited."""
    before = {m.get("ts"): m for m in old.get("messages", [])}
    for m in new.get("messages", []):
        prev = before.get(m.get("ts"))
        if prev is None:
            yield ("comment" if m.get("kind") == "comment" else "reply" if m.get("reply_to") else "post"), m
        elif prev.get("edited") != m.get("edited") and m.get("edited"):
            yield "edit", m


def plan(old, new, handles):
    by_ts = {m.get("ts"): m for m in new.get("messages", [])}
    subs = new.get("subscriptions", {})
    out = []
    for event, m in changes(old, new):
        if m.get("hidden"):
            continue
        # alerts from the listener are board-internal
        if m.get("session") in ("Network@NHI.com", "IT@NHI.com", "ITSupport@NHI.com") and event == "post":
            continue
        root = root_of(m, by_ts)
        if m.get("dm_to"):
            # DMs only ever go to the two people in them
            people = {m["dm_to"], root.get("session"), root.get("dm_to")}
        else:
            people = set(subs.get(root.get("ts"), [])) | tags_of(m, handles)
            if event in ("reply", "comment"):
                parent = by_ts.get(m.get("reply_to"))
                if parent:
                    people.add(parent.get("session"))
        people.discard(m.get("session"))
        people.discard(None)
        if not people:
            continue
        out.append({
            "event": event,
            "to": sorted(people),
            "from": m.get("session", "?"),
            "subject": root.get("subject") or "(no subject)",
            "link": thread_link(root.get("ts"), m.get("ts")),
            "msg": m,
        })
    return out


def render(n):
    verb = {"post": "posted", "reply": "replied", "comment": "commented", "edit": "edited a message"}[n["event"]]
    subj = f"[Board] {n['from']} {verb}: {n['subject']}"
    body = (
        f"{n['from']} {verb} in \"{n['subject']}\".\n\n"
        f"{n['msg'].get('msg', '')[:600]}\n\n"
        f"Open the thread: {n['link']}\n\n"
        "You get this because you follow the thread, were tagged, or it's a DM to you.\n"
        "Unfollow from the thread page (🔔 Following).\n"
    )
    return subj, body


def send(notes, contacts):
    host = os.environ.get("SMTP_HOST")
    live = os.environ.get("NOTIFY_SEND") == "1" and host
    smtp = None
    if live:
        smtp = smtplib.SMTP(host, int(os.environ.get("SMTP_PORT", "587")))
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(os.environ.get("SMTP_USER", ""), os.environ.get("SMTP_PASS", ""))
    sent = 0
    for n in notes:
        subj, body = render(n)
        for handle in n["to"]:
            addr = contacts.get(handle)
            if not addr:
                print(f"[notify] {n['event']} -> {handle}: no email on file, skipped")
                continue
            if not live:
                print(f"[notify] DRY RUN {n['event']} -> {handle}: {subj}")
                continue
            em = EmailMessage()
            em["From"] = os.environ.get("NOTIFY_FROM", os.environ.get("SMTP_USER", ""))
            em["To"] = addr
            em["Subject"] = subj
            em.set_content(body)
            smtp.send_message(em)
            sent += 1
            print(f"[notify] sent {n['event']} -> {handle}")
    if smtp:
        smtp.quit()
    return sent


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: notify.py OLD.json NEW.json")
    old, new = load(sys.argv[1]), load(sys.argv[2])
    try:
        contacts = json.loads(os.environ.get("NOTIFY_CONTACTS") or "{}")
    except ValueError:
        contacts = {}
    handles = set(contacts) | {m.get("session", "") for m in new.get("messages", [])}
    handles.discard("")
    notes = plan(old, new, handles)
    print(f"[notify] {len(notes)} notification(s)")
    send(notes, contacts)
