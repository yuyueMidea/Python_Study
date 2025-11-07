#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Outlook Feedback Export + Mail Sender (Win32 Dispatch / MAPI)
- 抓取本机 Outlook 邮件（按 subject/sender 过滤）
- 解析问卷文本为结构化数据
- 导出 Excel 报表 report.xlsx
- 通过 Outlook 发送报表到目标邮箱（含一次性 Token）
- 自检：
  1) 抓取/解析是否产出数据
  2) Excel 是否成功生成（存在且非空）
  3) 邮件是否发送成功（在“已发送邮件”中回查 Subject Token）

注意：
- 需要本机安装并登录可用的 Outlook 客户端
- 使用 win32com（pywin32）驱动 Outlook MAPI
"""

# ========================== 配置区（按需修改） ==========================
# 读取位置：支持 "Inbox" 或 "Inbox\\Sub1\\Sub2"
OUTLOOK_FOLDER_PATH = "Inbox"
# 最多处理多少封（从最近往前数）
SHOW_LIMIT = 500
# 主题关键词（小写匹配）
SUBJECT_KEYWORDS = ["feedback", "survey"]
# 发件人白名单（可留空=不限制），例：["noreply@typeform.com"]
SURVEY_SENDERS = []

# 导出
REPORT_XLSX = "report.xlsx"

# 邮件发送配置 —— <<< 按需修改 >>>
TARGET_TO = ["someone@example.com"]   # 收件人
TARGET_CC = []                        # 抄送（可空）
TARGET_BCC = []                       # 密送（可空）
MAIL_SUBJECT_PREFIX = "Feedback Report"
MAIL_BODY_TEXT = (
    "Hi,\n\n"
    "Please find attached the latest feedback report exported from Outlook.\n"
    "This email was sent automatically by the local script.\n\n"
    "Regards,\nAutomated Reporter"
)

# 发送后在“已发送邮件”中回查的超时（秒）
SENT_CHECK_TIMEOUT = 45
SENT_CHECK_INTERVAL = 3

# ========================== 依赖与导入 ==========================
import os
import re
import sys
import time
import uuid
from datetime import datetime
from typing import List, Dict, Tuple
import pandas as pd

# win32 相关
try:
    import win32com.client as win32
    from win32com.client import constants
except Exception:
    print("请先安装 pywin32： pip install pywin32")
    raise

# ========================== 工具函数（解码/抽正文/过滤） ==========================
REPORT_COLUMNS = [
    "Ref ID",
    "Q1 Score","Q1 Text",
    "Q2 Score","Q2 Text",
    "Q3 Score","Q3 Text",
    "Q4 Score","Q4 Text",
    "Q5 Score","Q5 Text",
    "Submit Date","Submit Time"
]

def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()

def subject_sender_filter(subj: str, frm: str) -> bool:
    s = (subj or "").lower()
    f = (frm or "").lower()
    subject_hit = any(k in s for k in SUBJECT_KEYWORDS) if SUBJECT_KEYWORDS else True
    sender_hit = True if not SURVEY_SENDERS else any(x in f for x in SURVEY_SENDERS)
    return subject_hit and sender_hit

# ========================== 解析规则（沿用既有实现） ==========================
RE_SUBMIT = re.compile(
    r"submit\s*date\s*:\s*(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*[-–—]\s*(?P<time>\d{1,2}:\d{2})",
    re.IGNORECASE
)
RE_REFID  = re.compile(r"ref\s*id\s*[:#-]?\s*(?P<id>[A-Za-z0-9_-]+)", re.IGNORECASE)
RE_QA     = re.compile(r"^(?:Q\s*)?(?P<num>[1-5])\s*(?P<sub>[ab])\s*[:\-\)\.]\s*(?P<val>.+?)\s*$", re.IGNORECASE)

def _parse_submit_block(text: str) -> Tuple[str,str]:
    m = RE_SUBMIT.search(text or "")
    if not m: return "",""
    raw_date, raw_time = m.group("date").strip(), m.group("time").strip()
    d,mn,y = re.split(r"[/-]", raw_date)
    if len(y)==2: y="20"+y
    d,mn = d.zfill(2), mn.zfill(2)
    try:
        _ = int(y); _ = int(d); _ = int(mn)
        std_date = f"{d}/{mn}/{y}"
    except Exception:
        std_date = raw_date
    hh,mm = raw_time.split(":")
    return std_date, f"{hh.zfill(2)}:{mm.zfill(2)}"

def _parse_refid(text: str) -> str:
    m = RE_REFID.search(text or "")
    return m.group("id").strip() if m else ""

def _parse_answers(text: str) -> Dict[str,str]:
    ans={}
    for raw in (text or "").splitlines():
        line=raw.strip()
        if not line: continue
        m=RE_QA.match(line)
        if m:
            k=f"{m.group('num').lower()}{m.group('sub').lower()}"
            ans[k]=m.group("val").strip()
    return ans

def parse_single_body(body: str) -> Dict[str,str]:
    ref_id=_parse_refid(body)
    sdate, stime=_parse_submit_block(body)
    ans=_parse_answers(body)
    return {
        "Ref ID": ref_id,
        "Q1 Score": ans.get("1a",""), "Q1 Text": ans.get("1b",""),
        "Q2 Score": ans.get("2a",""), "Q2 Text": ans.get("2b",""),
        "Q3 Score": ans.get("3a",""), "Q3 Text": ans.get("3b",""),
        "Q4 Score": ans.get("4a",""), "Q4 Text": ans.get("4b",""),
        "Q5 Score": ans.get("5a",""), "Q5 Text": ans.get("5b",""),
        "Submit Date": sdate, "Submit Time": stime,
    }

# ========================== MAPI：解析 Outlook 文件夹/抓取邮件 ==========================
def _resolve_folder(namespace, path: str):
    """
    解析类似 'Inbox' 或 'Inbox\\Sub1\\Sub2' 的路径到 MAPIFolder。
    默认从当前配置文件的收件箱向下解析。
    """
    folder = namespace.GetDefaultFolder(constants.olFolderInbox)  # 6
    if not path or path.lower() == "inbox":
        return folder

    parts = [p for p in path.split("\\") if p]
    if parts and parts[0].lower() == "inbox":
        parts = parts[1:]

    for name in parts:
        folder = folder.Folders.Item(name)
    return folder

def fetch_outlook_messages(limit: int = SHOW_LIMIT, folder_path: str = OUTLOOK_FOLDER_PATH) -> List[str]:
    """
    使用 Outlook MAPI 读取邮件正文（返回纯文本 body 列表）
    - 从最近邮件往前遍历，命中过滤规则则加入结果，直到 limit
    - 优先取 MailItem.Body（纯文本）；若为空再用 HTMLBody 去标签
    """
    outlook = win32.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    folder = _resolve_folder(namespace, folder_path)

    items = folder.Items
    items.IncludeRecurrences = True
    items.Sort("[ReceivedTime]", True)

    bodies: List[str] = []
    taken = 0
    for item in items:
        if getattr(item, "Class", None) != 43:  # 43 = olMail
            continue

        subj = getattr(item, "Subject", "") or ""
        frm  = getattr(item, "SenderEmailAddress", "") or getattr(item, "SenderName", "") or ""

        if not subject_sender_filter(subj, frm):
            continue

        body = (getattr(item, "Body", None) or "").strip()
        if not body:
            html = getattr(item, "HTMLBody", None) or ""
            body = _strip_html(html)

        if body:
            bodies.append(body)
            taken += 1
            if taken >= limit:
                break

    return bodies

# ========================== 导出 Excel ==========================
def build_report_from_texts(texts: List[str], out_xlsx: str) -> pd.DataFrame:
    rows=[]
    for body in texts:
        try:
            rows.append(parse_single_body(body))
        except Exception:
            ref_id=_parse_refid(body)
            sdate,stime=_parse_submit_block(body)
            rows.append({
                "Ref ID": ref_id,
                "Q1 Score":"","Q1 Text":"",
                "Q2 Score":"","Q2 Text":"",
                "Q3 Score":"","Q3 Text":"",
                "Q4 Score":"","Q4 Text":"",
                "Q5 Score":"","Q5 Text":"",
                "Submit Date": sdate, "Submit Time": stime
            })

    df = pd.DataFrame(rows, columns=REPORT_COLUMNS)
    df = df.drop_duplicates(subset=["Ref ID","Submit Date","Submit Time"], keep="first")

    for col in ["Q1 Score","Q2 Score","Q3 Score","Q4 Score","Q5 Score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Survey")
    return df

# ========================== 发送报表（Outlook MAPI） ==========================
def send_report_via_outlook(
    report_path: str,
    to: List[str],
    cc: List[str],
    bcc: List[str],
    subject_prefix: str,
    body_text: str,
) -> Tuple[str, str]:
    """
    返回 (subject_with_token, token)
    """
    outlook = win32.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")

    token = f"[FEEDBACK-REPORT:{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}]"
    subject = f"{subject_prefix} {token}"

    mail = outlook.CreateItem(0)  # 0 = olMailItem
    if to:  mail.To  = ";".join(to)
    if cc:  mail.CC  = ";".join(cc)
    if bcc: mail.BCC = ";".join(bcc)
    mail.Subject = subject
    mail.Body = body_text

    abs_path = os.path.abspath(report_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"附件不存在：{abs_path}")
    mail.Attachments.Add(Source=abs_path)

    # 发送
    mail.Send()

    return subject, token

def _find_recent_sent_by_token(namespace, token: str) -> bool:
    """在已发送邮件中查找包含 token 的主题。"""
    sent_folder = namespace.GetDefaultFolder(constants.olFolderSentMail)  # 5
    items = sent_folder.Items
    items.Sort("[SentOn]", True)
    checked = 0
    for item in items:
        if getattr(item, "Class", None) != 43:
            continue
        subj = getattr(item, "Subject", "") or ""
        if token in subj:
            return True
        checked += 1
        if checked >= 100:  # 只看最近 100 封，足够判断
            break
    return False

def wait_sent_verification(token: str, timeout: int = SENT_CHECK_TIMEOUT, interval: int = SENT_CHECK_INTERVAL) -> bool:
    """循环回查“已发送邮件”是否出现 token。"""
    outlook = win32.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    deadline = time.time() + max(1, timeout)
    while time.time() < deadline:
        if _find_recent_sent_by_token(namespace, token):
            return True
        time.sleep(max(1, interval))
    return False

# ========================== 主流程 & 自检 ==========================
def main():
    print("== Outlook Feedback Export + Mail Sender (win32/MAPI) ==")

    # 1) 抓取
    try:
        texts = fetch_outlook_messages(limit=SHOW_LIMIT, folder_path=OUTLOOK_FOLDER_PATH)
    except Exception as e:
        print("拉取失败：", e)
        sys.exit(2)

    print(f"匹配到 {len(texts)} 封（按主题/发件人过滤后）。正在生成报表…")
    if not texts:
        print("没有符合条件的邮件（主题需包含 feedback/survey）。")
        sys.exit(1)

    # 2) 生成报表
    df = build_report_from_texts(texts, REPORT_XLSX)
    rows = len(df)
    print(f"导出完成：{REPORT_XLSX}（{rows} 行）")

    # 3) 自检（导出）
    file_ok = os.path.exists(REPORT_XLSX) and os.path.getsize(REPORT_XLSX) > 0 and rows > 0
    print("Self-check[Export]:", "PASS ✅" if file_ok else "FAIL ❌")
    if not file_ok:
        sys.exit(3)

    # 4) 发送报表
    try:
        subject, token = send_report_via_outlook(
            report_path=REPORT_XLSX,
            to=TARGET_TO,
            cc=TARGET_CC,
            bcc=TARGET_BCC,
            subject_prefix=MAIL_SUBJECT_PREFIX,
            body_text=MAIL_BODY_TEXT,
        )
        print(f"已提交发送：{subject}")
    except Exception as e:
        print("发送失败：", e)
        sys.exit(4)

    # 5) 自检（发送是否进入“已发送”）
    ok_sent = wait_sent_verification(token)
    print("Self-check[Mail Sent]:", "PASS ✅" if ok_sent else "FAIL ❌")

    overall_ok = file_ok and ok_sent
    print("Overall:", "PASS ✅" if overall_ok else "PARTIAL ⚠️")
    sys.exit(0 if overall_ok else 5)

if __name__ == "__main__":
    main()
