#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
feedback_daily.py — 单文件：拉取邮件 → 解析 → 生成 report.xlsx → SMTP 发送

- IMAP 优先；若 126/163 返回 "Unsafe Login"（EXAMINE/SELECT），自动 POP3 兜底
- 仅匹配指定主题关键词/发件人的邮件
- 解析正文格式：
    eFrom submit date: 25/06/2025 - 11:52
    Ref ID: UMD00089xxx
    1a:5
    1b:xxx
    ...
    5a:4
    5b:xxx
- 输出 Excel 列顺序固定为：
    Ref ID | Q1 Score | Q1 Text | Q2 Score | Q2 Text | Q3 Score | Q3 Text | Q4 Score | Q4 Text | Q5 Score | Q5 Text | Submit Date | Submit Time
"""

# ============================ 配置区（按需填写） ============================
# 源邮箱（用于收取反馈）
IMAP_HOST = "imap.126.com"
IMAP_PORT_SSL = 993
POP3_HOST = "pop.126.com"
POP3_PORT_SSL = 995
MAIL_USER = "yy18825237023@126.com"     # 源邮箱账号
MAIL_PASS = "EDuaH3BumbLK7HEi"
# "在126后台生成的客户端授权码"  # 源邮箱“客户端授权码”（不是登录密码）

# 抓取与过滤
SHOW_LIMIT = 200          # 最多处理多少封（用于 IMAP/POP3 末端切片）
POP3_MAX_FETCH = 500      # POP3 扫描历史上限（避免一次拉太多）
SUBJECT_KEYWORDS = ["feedback", "survey"]   # 主题关键词（小写比较，包含即命中）
SURVEY_SENDERS = []       # 发件人白名单（可留空=不限制），如：["noreply@xxx.com"]

# 报表
REPORT_XLSX = "report.xlsx"

# 发送设置（SMTP 用于发送报表）
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465           # 465=SSL；587=STARTTLS
SMTP_USE_SSL = True
SMTP_USE_TLS = False
SMTP_USERNAME = MAIL_USER
SMTP_PASSWORD = MAIL_PASS
SMTP_FROM = MAIL_USER     # 发件人
REPORT_TO = ["18825237023@163.com"]  # 收件人（可多）
REPORT_CC = []            # 抄送
REPORT_BCC = []           # 密送
SUBJECT_LINE = "Daily Survey Feedback Report"

# ============================ 依赖与导入 ============================
import os, re, sys, ssl, time, socket, poplib, imaplib, email, mimetypes
from pathlib import Path
from typing import List, Dict, Tuple, Iterable, Union
from email import policy
from email.parser import BytesParser
from email.header import decode_header
from email.message import EmailMessage
from email.utils import formatdate
import smtplib
import pandas as pd

# ============================ 工具函数：通用 ============================
REPORT_COLUMNS = [
    "Ref ID",
    "Q1 Score", "Q1 Text",
    "Q2 Score", "Q2 Text",
    "Q3 Score", "Q3 Text",
    "Q4 Score", "Q4 Text",
    "Q5 Score", "Q5 Text",
    "Submit Date", "Submit Time"
]

def _decode_header_value(raw: str) -> str:
    if not raw: return ""
    parts = decode_header(raw); out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            try: out.append(part.decode(enc or "utf-8", errors="ignore"))
            except Exception: out.append(part.decode("utf-8", errors="ignore"))
        else:
            out.append(part)
    return "".join(out)

def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_plain_text(msg: email.message.Message) -> str:
    """优先 text/plain；若仅 HTML 则粗略去标签"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart": continue
            if part.get_content_disposition() == "attachment": continue
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                try: return payload.decode(charset, errors="ignore").strip()
                except Exception: return payload.decode("utf-8", errors="ignore").strip()
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                try: html = payload.decode(charset, errors="ignore")
                except Exception: html = payload.decode("utf-8", errors="ignore")
                return _strip_html(html)
        return ""
    else:
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        try: text = payload.decode(charset, errors="ignore")
        except Exception: text = payload.decode("utf-8", errors="ignore")
        return _strip_html(text) if text.strip().startswith("<") else text.strip()

def subject_sender_filter(subject: str, from_header: str) -> bool:
    s = (subject or "").lower()
    f = (from_header or "").lower()
    subject_hit = any(k in s for k in SUBJECT_KEYWORDS) if SUBJECT_KEYWORDS else True
    sender_hit = (not SURVEY_SENDERS) or any(sn in f for sn in SURVEY_SENDERS)
    return subject_hit and sender_hit

# ============================ 拉取：IMAP → POP3 ============================
def _send_imap_id(conn: imaplib.IMAP4_SSL):
    """部分网易节点对报 RFC2971 ID 的客户端更友好"""
    try:
        typ, caps = conn.capability()
        cap_bytes = b" ".join(caps or [])
        if b"ID" in cap_bytes.upper():
            args = '("name" "Microsoft Outlook" "version" "16.0" "vendor" "Microsoft" "os" "Windows 10")'
            conn._simple_command("ID", args); conn._get_response()
            args2 = '("name" "FeedbackBot" "version" "1.0")'
            conn._simple_command("ID", args2); conn._get_response()
    except Exception:
        pass

def try_imap_fetch(limit: int = SHOW_LIMIT) -> List[email.message.Message]:
    ctx = ssl.create_default_context()
    with imaplib.IMAP4_SSL(host=IMAP_HOST, port=IMAP_PORT_SSL, ssl_context=ctx) as conn:
        conn.login(MAIL_USER, MAIL_PASS)
        _send_imap_id(conn)

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

        msgs = []
        for eid in id_list[-limit:]:
            typ, raw = conn.fetch(eid, "(RFC822)")
            if typ == "OK" and raw and isinstance(raw[0], tuple):
                msg = email.message_from_bytes(raw[0][1], policy=policy.default)
                subj = _decode_header_value(msg.get("Subject"))
                frm = msg.get("From") or ""
                if subject_sender_filter(subj, frm):
                    msgs.append(msg)
        return msgs

def try_pop3_fetch(limit: int = SHOW_LIMIT, max_fetch: int = POP3_MAX_FETCH) -> List[email.message.Message]:
    """兼容不支持 with 的 Python：手动 quit()"""
    msgs: List[email.message.Message] = []
    pop = None
    try:
        pop = poplib.POP3_SSL(POP3_HOST, POP3_PORT_SSL, timeout=30)
        pop.user(MAIL_USER); pop.pass_(MAIL_PASS)
    except Exception as e_ssl:
        if pop:
            try: pop.quit()
            except Exception: pass
        try:
            pop = poplib.POP3(POP3_HOST, 110, timeout=30)
            pop.user(MAIL_USER); pop.pass_(MAIL_PASS)
            try: pop.stls()
            except Exception: pass
        except Exception as e_plain:
            raise RuntimeError(f"POP3 connect failed: {e_ssl} | {e_plain}")

    try:
        count, _ = pop.stat()
        if count <= 0:
            return []
        start = max(1, count - max_fetch + 1)
        indices = list(range(max(start, count - limit + 1), count + 1))
        for i in indices:
            resp, lines, octets = pop.retr(i)
            raw = b"\r\n".join(lines)
            msg = BytesParser(policy=policy.default).parsebytes(raw)
            subj = _decode_header_value(msg.get("Subject"))
            frm = msg.get("From") or ""
            if subject_sender_filter(subj, frm):
                msgs.append(msg)
        return msgs
    finally:
        if pop:
            try: pop.quit()
            except (socket.error, poplib.error_proto, Exception):
                pass

# ============================ 解析：正文 → 结构化 ============================
RE_SUBMIT = re.compile(
    r"submit\s*date\s*:\s*(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*[-–—]\s*(?P<time>\d{1,2}:\d{2})",
    re.IGNORECASE
)
RE_REFID  = re.compile(r"ref\s*id\s*[:#-]?\s*(?P<id>[A-Za-z0-9_-]+)", re.IGNORECASE)
RE_QA     = re.compile(r"^(?:Q\s*)?(?P<num>[1-5])\s*(?P<sub>[ab])\s*[:\-\)\.]\s*(?P<val>.+?)\s*$", re.IGNORECASE)

def _parse_submit_block(text: str) -> Tuple[str, str]:
    m = RE_SUBMIT.search(text)
    if not m: return "", ""
    raw_date, raw_time = m.group("date").strip(), m.group("time").strip()
    d, mn, y = re.split(r"[/-]", raw_date)
    if len(y) == 2: y = "20" + y
    d, mn = d.zfill(2), mn.zfill(2)
    try:
        _ = int(y); _ = int(d); _ = int(mn)
        std_date = f"{d}/{mn}/{y}"
    except Exception:
        std_date = raw_date
    hh, mm = raw_time.split(":")
    return std_date, f"{hh.zfill(2)}:{mm.zfill(2)}"

def _parse_refid(text: str) -> str:
    m = RE_REFID.search(text)
    return m.group("id").strip() if m else ""

def _parse_answers(text: str) -> Dict[str, str]:
    ans: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line: continue
        m = RE_QA.match(line)
        if m:
            k = f"{m.group('num').lower()}{m.group('sub').lower()}"
            ans[k] = m.group("val").strip()
    return ans

def parse_single_body(body: str) -> Dict[str, str]:
    ref_id = _parse_refid(body)
    sdate, stime = _parse_submit_block(body)
    ans = _parse_answers(body)
    row = {
        "Ref ID": ref_id,
        "Q1 Score": ans.get("1a",""), "Q1 Text": ans.get("1b",""),
        "Q2 Score": ans.get("2a",""), "Q2 Text": ans.get("2b",""),
        "Q3 Score": ans.get("3a",""), "Q3 Text": ans.get("3b",""),
        "Q4 Score": ans.get("4a",""), "Q4 Text": ans.get("4b",""),
        "Q5 Score": ans.get("5a",""), "Q5 Text": ans.get("5b",""),
        "Submit Date": sdate, "Submit Time": stime,
    }
    return row

def build_report_from_messages(msgs: List[email.message.Message], out_xlsx: str) -> pd.DataFrame:
    texts: List[str] = [extract_plain_text(m) for m in msgs]
    rows: List[Dict[str,str]] = []
    for t in texts:
        try:
            rows.append(parse_single_body(t))
        except Exception:
            ref_id = _parse_refid(t)
            sdate, stime = _parse_submit_block(t)
            rows.append({"Ref ID": ref_id, "Q1 Score":"","Q1 Text":"","Q2 Score":"","Q2 Text":"",
                         "Q3 Score":"","Q3 Text":"","Q4 Score":"","Q4 Text":"","Q5 Score":"","Q5 Text":"",
                         "Submit Date":sdate,"Submit Time":stime})
    df = pd.DataFrame(rows, columns=REPORT_COLUMNS)
    df = df.drop_duplicates(subset=["Ref ID","Submit Date","Submit Time"], keep="first")
    for col in ["Q1 Score","Q2 Score","Q3 Score","Q4 Score","Q5 Score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Survey")
    return df

# ============================ SMTP 发送 ============================
def send_report(subject: str, body_text: str, attachments: Iterable[Union[str,Path]]) -> str:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = ", ".join(REPORT_TO)
    if REPORT_CC: msg["Cc"] = ", ".join(REPORT_CC)
    rcpts = list(dict.fromkeys(REPORT_TO + REPORT_CC + REPORT_BCC))
    msg["Date"] = formatdate(localtime=True)
    msg.set_content(body_text)

    for pth in attachments or []:
        p = Path(pth)
        if not p.exists(): raise FileNotFoundError(f"Attachment not found: {p}")
        ctype, enc = mimetypes.guess_type(str(p))
        if ctype is None or enc is not None: ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with p.open("rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=p.name)

    attempt, max_retries, backoff = 0, 3, 1.5
    last_err = None
    while attempt <= max_retries:
        try:
            if SMTP_USE_SSL:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30, context=context)
            else:
                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
            server.ehlo()
            if SMTP_USE_TLS and not SMTP_USE_SSL:
                context = ssl.create_default_context()
                server.starttls(context=context); server.ehlo()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            resp = server.sendmail(SMTP_FROM, rcpts, msg.as_string())
            server.quit()
            if resp:
                raise smtplib.SMTPException(f"Partial failure: {resp}")
            return "OK"
        except (smtplib.SMTPException, OSError) as e:
            last_err = e
            if attempt == max_retries:
                raise
            time.sleep((backoff ** attempt) + 0.5)
            attempt += 1
    raise RuntimeError(f"Failed to send after retries: {last_err}")

# ============================ 主流程与自检 ============================
def main():
    print("== Feedback Daily (Single-File) ==")
    # 1) 拉取
    try:
        msgs = try_imap_fetch(limit=SHOW_LIMIT)
        source = "IMAP"
    except Exception as e:
        print(f"[IMAP blocked/failed] {e}\n→ Falling back to POP3...")
        msgs = try_pop3_fetch(limit=SHOW_LIMIT, max_fetch=POP3_MAX_FETCH)
        source = "POP3"

    if not msgs:
        print("No matched messages. Quit.")
        sys.exit(1)

    print(f"Fetched {len(msgs)} messages via {source}. Building report...")

    # 2) 生成报表
    df = build_report_from_messages(msgs, out_xlsx=REPORT_XLSX)
    rows = len(df)
    print(f"Report saved: {REPORT_XLSX} (rows={rows})")

    # 3) 发送
    body = f"""Daily Survey Feedback Report

Source: {source}
Rows: {rows}
File: {Path(REPORT_XLSX).resolve()}
"""
    status = send_report(subject=SUBJECT_LINE, body_text=body, attachments=[REPORT_XLSX])
    print("Send status:", status)

    # 4) 自检（至少有 1 行 + 发送成功）
    ok = rows > 0 and status == "OK"
    print("Self-check:", "PASS ✅" if ok else "FAIL ❌")
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    # 轻量输入校验
    if not MAIL_USER or not MAIL_PASS:
        print("请在脚本顶部配置源邮箱账号与“客户端授权码”。"); sys.exit(2)
    if not REPORT_TO:
        print("请在脚本顶部配置 REPORT_TO 收件人列表。"); sys.exit(2)
    main()
