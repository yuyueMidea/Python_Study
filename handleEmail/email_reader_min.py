
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Minimal Email Reader (IMAP→POP3 fallback)

- Prioritizes IMAP; if blocked by 126/163 'Unsafe Login', automatically falls back to POP3.
- Prints concise summaries of the latest N emails.
- Designed to be small, dependency-free (standard library only).
"""

import imaplib
import poplib
import email
import re
import sys
import ssl
from email.header import decode_header
from email import policy
from email.parser import BytesParser
from getpass import getpass

# ============== Config ==============
IMAP_HOST = "imap.126.com"
POP3_HOST = "pop.126.com"
PORT_IMAP_SSL = 993
PORT_POP3_SSL = 995
USERNAME = "yy18825237023@126.com"  # fill or leave empty to prompt
PASSWORD = ""  # app password is recommended

# How many recent emails to show
SHOW_LIMIT = 11
# Max POP3 fetch in fallback
POP3_MAX_FETCH = 200

# ============== Helpers ==============
def _decode_header_value(raw):
    if not raw:
        return ""
    parts = decode_header(raw)
    out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                out.append(part.decode(enc or "utf-8", errors="ignore"))
            except Exception:
                out.append(part.decode("utf-8", errors="ignore"))
        else:
            out.append(part)
    return "".join(out)

def _extract_body(msg):
    """Return plaintext body; if only HTML, strip tags naively."""
    def strip_html(html):
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    if msg.is_multipart():
        # prefer text/plain
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                try:
                    return payload.decode(charset, errors="ignore").strip()
                except Exception:
                    return payload.decode("utf-8", errors="ignore").strip()
        # fallback to first text/html
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                try:
                    html = payload.decode(charset, errors="ignore")
                except Exception:
                    html = payload.decode("utf-8", errors="ignore")
                return strip_html(html)
        return ""
    else:
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="ignore")
        except Exception:
            text = payload.decode("utf-8", errors="ignore")
        if text.strip().startswith("<"):
            return strip_html(text)
        return text.strip()

def _send_imap_id(conn):
    """Send RFC2971 ID (some providers relax checks when a client ID is sent)."""
    try:
        typ, caps = conn.capability()
        cap_bytes = b" ".join(caps or [])
        if b"ID" in cap_bytes.upper():
            args = '("name" "Microsoft Outlook" "version" "16.0" "vendor" "Microsoft" "os" "Windows 10")'
            conn._simple_command("ID", args); conn._get_response()
            args2 = '("name" "MinimalEmailReader" "version" "1.0")'
            conn._simple_command("ID", args2); conn._get_response()
    except Exception:
        pass

# ============== IMAP path ==============
def try_imap_fetch(user, pwd, host=IMAP_HOST, port=PORT_IMAP_SSL, limit=SHOW_LIMIT):
    ctx = ssl.create_default_context()
    with imaplib.IMAP4_SSL(host=host, port=port, ssl_context=ctx) as conn:
        conn.login(user, pwd)
        _send_imap_id(conn)

        # Prefer EXAMINE (readonly), then fallback to SELECT
        typ, data = conn.select("INBOX", readonly=True)
        if typ != "OK":
            typ2, data2 = conn.select("INBOX", readonly=False)
            if typ2 != "OK":
                reason = (data2[0].decode(errors="ignore") if data2 and isinstance(data2[0], (bytes, bytearray)) else str(data2))
                raise RuntimeError(f"IMAP select failed: {reason}")

        typ, ids = conn.search(None, "ALL")
        if typ != "OK":
            raise RuntimeError("IMAP search failed")
        id_list = ids[0].split()
        if not id_list:
            return []

        # Fetch last N
        msgs = []
        for eid in id_list[-limit:]:
            typ, raw = conn.fetch(eid, "(RFC822)")
            if typ == "OK" and raw and isinstance(raw[0], tuple):
                msg = email.message_from_bytes(raw[0][1], policy=policy.default)
                msgs.append(msg)
        return msgs

# ============== POP3 fallback ==============
import socket

def try_pop3_fetch(user, pwd, host=POP3_HOST, port=PORT_POP3_SSL,
                   limit=SHOW_LIMIT, max_fetch=POP3_MAX_FETCH):
    """POP3 拉取最近 limit 封（max_fetch 为最大检索范围）；兼容不支持 with 的 Python。"""
    msgs = []

    # 优先 POP3 over SSL (995)
    pop = None
    try:
        pop = poplib.POP3_SSL(host, port, timeout=30)
        pop.user(user); pop.pass_(pwd)
    except Exception as e_ssl:
        # 回退：POP3 110 + STLS
        if pop:
            try: pop.quit()
            except Exception: pass
        try:
            pop = poplib.POP3(host, 110, timeout=30)
            pop.user(user); pop.pass_(pwd)
            # 有些服务器支持 STLS，可尝试升级
            try:
                pop.stls()  # 如果不支持会抛异常，忽略即可
            except Exception:
                pass
        except Exception as e_plain:
            raise RuntimeError(f"POP3 连接失败（SSL 与明文均不可用）：{e_ssl} | {e_plain}")

    try:
        count, _ = pop.stat()
        if count <= 0:
            return []
        
        print(f"[POP3] server message count = {count}")
        resp, listing, _ = pop.list()
        print(f"[POP3] LIST size = {len(listing)} (first few: {listing[:5]})")


        start = max(1, count - max_fetch + 1)
        # 只拿最后 limit 封用于展示
        last_indices = list(range(max(start, count - limit + 1), count + 1))

        for i in last_indices:
            resp, lines, octets = pop.retr(i)
            raw = b"\r\n".join(lines)
            msg = BytesParser(policy=policy.default).parsebytes(raw)
            msgs.append(msg)
        return msgs
    finally:
        if pop:
            try:
                pop.quit()
            except (socket.error, poplib.error_proto, Exception):
                pass

# ============== Main runner ==============
def summarize(msg):
    subject = _decode_header_value(msg.get("Subject"))
    from_ = msg.get("From") or ""
    date_ = msg.get("Date") or ""
    body = _extract_body(msg)
    preview = (body[:200] + ("..." if len(body) > 200 else "")) if body else ""
    print(f"===• {subject or '（无主题）'} | {from_} | {date_}===")
    if preview:
        print(f"  {preview}")

def self_check(messages):
    """Return True if at least one message has a non-empty body."""
    return any((_extract_body(m).strip() for m in messages))

def main():
    print("== Minimal Email Reader (IMAP→POP3 fallback) ==")
    user = USERNAME or input("Email: ").strip()
    pwd = PASSWORD or getpass("App Password: ")

    # 1) Try IMAP
    try:
        msgs = try_imap_fetch(user, pwd)
        source = "IMAP"
    except Exception as e:
        print(f"[IMAP blocked/failed] {e}\n→ Falling back to POP3...")
        msgs = try_pop3_fetch(user, pwd)
        source = "POP3"

    if not msgs:
        print("No messages found.")
        sys.exit(1)

    print(f"Fetched {len(msgs)} messages via {source}. Showing latest {len(msgs)}:" )
    for m in msgs:
        summarize(m)

    ok = self_check(msgs)
    print("\nSelf-check:", "PASS ✅" if ok else "FAIL ❌")
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
