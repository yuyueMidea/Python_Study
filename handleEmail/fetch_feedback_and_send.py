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
# 开始时间和结束时间
DATE_FROM = "2025-11-06"
DATE_TO = "2025-11-06"
# 主题关键词（小写匹配）
SUBJECT_KEYWORDS = ["feedback", "survey"]
# 发件人白名单（可留空=不限制），例：["noreply@typeform.com"]
SURVEY_SENDERS = []

# 导出的 Excel 文件名
REPORT_XLSX = "report.xlsx"

# 发送报表的邮件配置
TARGET_TO = ["someone@example.com"]
TARGET_CC = []
TARGET_BCC = []
MAIL_SUBJECT_PREFIX = "[Feedback Report]"
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
from typing import List, Dict, Tuple, Optional, Iterable
import pandas as pd
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# win32 相关
try:
    import win32com.client as win32
except Exception:
    print("请先安装 pywin32： pip install pywin32")
    raise

import pywintypes
import pythoncom

# ========================== 工具函数（解码/抽正文/过滤） ==========================
REPORT_COLUMNS = [
    "Ref ID",
    "Q1 Score",
    "Q1 Text",
    "Q2 Score",
    "Q2 Text",
    "Q3 Score",
    "Q3 Text",
    "Q4 Score",
    "Q4 Text",
    "Q5 Score",
    "Q5 Text",
    "Submit Date",
    "Submit Time",
]


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


def subject_sender_filter(subj: str, frm: str) -> bool:
    s = (subj or "").lower()
    f = (frm or "").lower()
    if SUBJECT_KEYWORDS:
        if not any(k in s for k in SUBJECT_KEYWORDS):
            return False
    if SURVEY_SENDERS:
        if f and not any(f.endswith(x.lower()) for x in SURVEY_SENDERS):
            return False
    return True


def _ensure_text(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8", "ignore")
        except Exception:
            return v.decode("latin1", "ignore")
    return str(v)


# ========================== 解析问卷文本 ==========================
RE_QA = re.compile(
    r"^\s*(?P<num>[Qq]?\d+)(?P<sub>[a-zA-Z])?\s*[:：]\s*(?P<val>.+?)\s*$"
)
RE_SUBMIT = re.compile(
    r"Submitted at\s*[:：]?\s*(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?P<time>\d{1,2}:\d{2})",
    re.IGNORECASE,
)
RE_REFID = re.compile(r"Ref(?:erence)?\s*ID\s*[:：]\s*(?P<id>\S+)", re.IGNORECASE)


def _parse_submit_block(text: str) -> Tuple[str, str]:
    m = RE_SUBMIT.search(text or "")
    if not m:
        return "", ""
    raw_date, raw_time = m.group("date").strip(), m.group("time").strip()
    d, mn, y = re.split(r"[/-]", raw_date)
    if len(y) == 2:
        y = "20" + y
    d, mn = d.zfill(2), mn.zfill(2)
    try:
        _ = int(y)
        _ = int(d)
        _ = int(mn)
        std_date = f"{d}/{mn}/{y}"
    except Exception:
        std_date = raw_date
    hh, mm = raw_time.split(":")
    return std_date, f"{hh.zfill(2)}:{mm.zfill(2)}"


def _parse_refid(text: str) -> str:
    m = RE_REFID.search(text or "")
    return m.group("id").strip() if m else ""


def _parse_answers(text: str) -> Dict[str, str]:
    ans = {}
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = RE_QA.match(line)
        if m:
            k = f"{m.group('num').lower()}{m.group('sub').lower()}"
            ans[k] = m.group("val").strip()
    return ans


def parse_single_body(body: str) -> Dict[str, str]:
    ref_id = _parse_refid(body)
    if not ref_id:
        return {}
    sdate, stime = _parse_submit_block(body)
    ans = _parse_answers(body)
    return {
        "Ref ID": ref_id,
        "Q1 Score": ans.get("1a", ""),
        "Q1 Text": ans.get("1b", ""),
        "Q2 Score": ans.get("2a", ""),
        "Q2 Text": ans.get("2b", ""),
        "Q3 Score": ans.get("3a", ""),
        "Q3 Text": ans.get("3b", ""),
        "Q4 Score": ans.get("4a", ""),
        "Q4 Text": ans.get("4b", ""),
        "Q5 Score": ans.get("5a", ""),
        "Q5 Text": ans.get("5b", ""),
        "Submit Date": sdate,
        "Submit Time": stime,
    }


# ========================== MAPI：常量 & 安全 COM 调用 ==========================
INBOX_ENUM = 6  # Inbox


def safe_com_call(func, *args, retries: int = 3, delay: float = 1.0, **kwargs):
    """
    对单次 COM 调用做重试，优先处理 'Call was rejected by callee' (RPC_E_CALL_REJECTED)。
    """
    last_exc = None
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except pywintypes.com_error as e:
            hresult = e.args[0] if e.args else None
            if hresult == -2147418111:  # RPC_E_CALL_REJECTED
                logger.warning(
                    f"COM 调用被 Outlook 拒绝 (RPC_E_CALL_REJECTED)，第 {i+1}/{retries} 次，稍后重试..."
                )
                last_exc = e
                if i < retries - 1:
                    time.sleep(delay)
                    continue
            # 不是该错误或重试用尽
            last_exc = e
            break
        except Exception as e:
            last_exc = e
            break
    # 所有重试失败
    raise last_exc


def _resolve_folder(namespace, folder_path: str):
    """
    支持 "Inbox" 或 "Inbox\\Sub1\\Sub2" 这样的路径。
    """
    if not folder_path:
        return namespace.GetDefaultFolder(INBOX_ENUM)
    parts = folder_path.split("\\")
    root = namespace.GetDefaultFolder(INBOX_ENUM) if parts[0].lower() == "inbox" else namespace.Folders[parts[0]]
    cur = root
    for p in parts[1:]:
        cur = cur.Folders[p]
    return cur


def _ensure_dt(v):
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v)
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return None
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(v, fmt)
            except Exception:
                pass
    return None


def _fmt_ol_datetime(dt: datetime) -> str:
    """
    格式为 Outlook Restrict 能识别的文本。通常 'YYYY-MM-DD HH:MM' 即可。
    """
    return dt.strftime("%Y-%m-%d %H:%M")


def _any_match(text: str, patterns: Iterable[str], ci: bool = True) -> bool:
    text = text or ""
    if ci:
        text = text.lower()
        patterns = [p.lower() for p in patterns]
    return any(p in text for p in patterns)


def _none_match(text: str, patterns: Iterable[str], ci: bool = True) -> bool:
    return not _any_match(text, patterns, ci)


def create_outlook_instance(max_retries: int = 3, retry_delay: float = 2.0):
    """
    创建稳健的 Outlook 实例，支持多种连接方式和重试机制。

    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）

    Returns:
        Outlook Application 对象
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            logger.info(f"尝试连接 Outlook (第 {attempt + 1} 次)...")

            # 方法1：尝试直接连接（最快）
            if attempt == 0:
                try:
                    outlook = safe_com_call(win32.Dispatch, "Outlook.Application")
                    logger.info("使用 Dispatch 连接成功")
                    return outlook
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Dispatch 连接失败: {e}")

            # 方法2：使用 EnsureDispatch（更稳定）
            if attempt <= 1:
                try:
                    outlook = safe_com_call(
                        win32.gencache.EnsureDispatch, "Outlook.Application"
                    )
                    logger.info("使用 EnsureDispatch 连接成功")
                    return outlook
                except Exception as e:
                    last_exception = e
                    logger.warning(f"EnsureDispatch 连接失败: {e}")

            # 方法3：使用动态调用（兼容性最好）
            try:
                outlook = safe_com_call(
                    win32.dynamic.Dispatch, "Outlook.Application"
                )
                logger.info("使用 dynamic.Dispatch 连接成功")
                return outlook
            except Exception as e:
                last_exception = e
                logger.warning(f"dynamic.Dispatch 连接失败: {e}")

            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_delay} 秒后重试连接 Outlook...")
                time.sleep(retry_delay)

        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.info(
                    f"连接尝试 {attempt + 1} 失败，等待后重试..."
                )
                time.sleep(retry_delay)

    # 所有尝试都失败
    error_msg = (
        f"无法连接 Outlook，{max_retries} 次尝试均失败。最后错误: {last_exception}"
    )
    logger.error(error_msg)
    raise Exception(error_msg)


def fetch_outlook_messages(
    limit: int = 500,
    folder_path: str = "Inbox",
    # 新增过滤条件：
    date_from=None,  # 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:MM' 或 datetime
    date_to=None,  # 同上
    senders: Optional[List[str]] = None,
    exclude_senders: Optional[List[str]] = None,
    subject_keywords: Optional[List[str]] = None,
    exclude_subject_keywords: Optional[List[str]] = None,
    body_keywords: Optional[List[str]] = None,
    exclude_body_keywords: Optional[List[str]] = None,
    case_insensitive: bool = True,
) -> List[str]:
    """
    从 Outlook 读取邮件正文（返回纯文本 body 列表），支持多种过滤条件。
    - 时间范围优先用 Items.Restrict 实现（性能更好）
    - 主题/发件人/正文的包含/排除在 Python 侧过滤
    """
    # 创建 Outlook 实例
    outlook = create_outlook_instance()
    # outlook = win32.Dispatch("Outlook.Application")
    namespace = safe_com_call(outlook.GetNamespace, "MAPI")
    folder = safe_com_call(_resolve_folder, namespace, folder_path)

    items = safe_com_call(lambda: folder.Items)
    items.IncludeRecurrences = True
    # 先按接收时间降序
    safe_com_call(items.Sort, "[ReceivedTime]", True)
    print("items_total_len: ", len(items))

    # ---------- 时间过滤（使用 Restrict） ----------
    df = _ensure_dt(date_from)
    dt = _ensure_dt(date_to)
    restricted = items
    filter_parts = []
    if df:
        filter_parts.append(f"[ReceivedTime] >= '{_fmt_ol_datetime(df)}'")
    if dt:
        filter_parts.append(f"[ReceivedTime] <= '{_fmt_ol_datetime(dt)}'")
    if filter_parts:
        restriction = " AND ".join(filter_parts)
        try:
            restricted = safe_com_call(items.Restrict, restriction)
        except Exception as e:
            # 若 Restrict 在个别区域设置下异常，降级为全量后Python侧过滤（但性能较差）
            restricted = items
            print(
                f"警告：Outlook Restrict 时间过滤失败，已降级为本地过滤。错误：{e}"
            )

    # ---------- 迭代并做关键词/发件人过滤 ----------
    bodies: List[str] = []
    taken = 0
    # 若未传 subject_keywords，则允许兼容脚本顶部默认 SUBJECT_KEYWORDS
    default_subject_kw = (
        subject_keywords
        if subject_keywords is not None
        else (globals().get("SUBJECT_KEYWORDS") or [])
    )

    count = len(restricted)
    for idx in range(1, count + 1):  # Outlook 集合是 1-based
        if limit and taken >= limit:
            break

        try:
            item = safe_com_call(restricted.Item, idx)
        except Exception as e:
            logger.warning(f"读取第 {idx} 封邮件失败：{e}")
            continue

        if getattr(item, "Class", None) != 43:  # 43 = olMail
            continue

        subj = getattr(item, "Subject", "") or ""
        frm = (
            getattr(item, "SenderEmailAddress", "")
            or getattr(item, "SenderName", "")
            or ""
        )

        # Python 侧的发件人与主题过滤（包含 + 排除）
        if senders and not _any_match(frm, senders, case_insensitive):
            continue
        if exclude_senders and not _none_match(
            frm, exclude_senders, case_insensitive
        ):
            continue

        # 主题包含/排除
        if default_subject_kw and not _any_match(
            subj, default_subject_kw, case_insensitive
        ):
            continue
        if exclude_subject_keywords and not _none_match(
            subj, exclude_subject_keywords, case_insensitive
        ):
            continue

        # 取正文（优先纯文本），必要时从 HTML 去标签
        body = (getattr(item, "Body", None) or "").strip()
        if not body:
            html = getattr(item, "HTMLBody", None) or ""
            body = _strip_html(html)

        if not body:
            continue

        # 正文包含/排除词
        if body_keywords and not _any_match(
            body, body_keywords, case_insensitive
        ):
            continue
        if exclude_body_keywords and not _none_match(
            body, exclude_body_keywords, case_insensitive
        ):
            continue

        bodies.append(body)
        taken += 1

    return bodies


# ========================== 导出 Excel ==========================
def build_report_from_texts(texts: List[str], out_xlsx: str) -> pd.DataFrame:
    rows = []
    for body in texts:
        try:
            txt_body = parse_single_body(body)
            if txt_body:
                rows.append(txt_body)
            else:
                rows.append({})
        except Exception:
            ref_id = _parse_refid(body)
            sdate, stime = _parse_submit_block(body)
            rows.append(
                {
                    "Ref ID": ref_id,
                    "Q1 Score": "",
                    "Q1 Text": "",
                    "Q2 Score": "",
                    "Q2 Text": "",
                    "Q3 Score": "",
                    "Q3 Text": "",
                    "Q4 Score": "",
                    "Q4 Text": "",
                    "Q5 Score": "",
                    "Q5 Text": "",
                    "Submit Date": sdate,
                    "Submit Time": stime,
                }
            )

    df = pd.DataFrame(rows, columns=REPORT_COLUMNS)
    df.to_excel(out_xlsx, index=False)
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
    使用 Outlook 发送报表，并在 subject 中附带一次性 token。
    返回 (subject, token)
    """
    outlook = create_outlook_instance()
    namespace = safe_com_call(outlook.GetNamespace, "MAPI")

    mail = safe_com_call(outlook.CreateItem, 0)  # 0 = olMailItem
    token = str(uuid.uuid4())[:8]
    subject = f"{subject_prefix} [{token}]"

    mail.Subject = subject
    mail.Body = body_text

    if to:
        mail.To = ";".join(to)
    if cc:
        mail.CC = ";".join(cc)
    if bcc:
        mail.BCC = ";".join(bcc)

    # 附件
    if report_path and os.path.exists(report_path):
        mail.Attachments.Add(os.path.abspath(report_path))

    mail.Send()
    return subject, token


def _find_recent_sent_by_token(namespace, token: str) -> bool:
    """在已发送邮件中查找包含 token 的主题。"""
    sent_folder = namespace.GetDefaultFolder(5)  # 5 = olFolderSentMail
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
        if checked >= 100:  # 只看最近 100 封即可
            break
    return False


def wait_sent_verification(token: str) -> bool:
    """
    发送后在“已发送邮件”中等待最多 SENT_CHECK_TIMEOUT 秒，确认有包含 token 的邮件。
    """
    outlook = create_outlook_instance()
    namespace = safe_com_call(outlook.GetNamespace, "MAPI")

    start_ts = time.time()
    while True:
        if _find_recent_sent_by_token(namespace, token):
            return True
        if time.time() - start_ts > SENT_CHECK_TIMEOUT:
            return False
        time.sleep(SENT_CHECK_INTERVAL)


# ========================== 主流程 ==========================
def main():
    print("== Outlook Feedback Export + Mail Sender (win32/MAPI) ==")

    # 1) 抓取
    try:
        texts = fetch_outlook_messages(
            limit=SHOW_LIMIT,
            folder_path=OUTLOOK_FOLDER_PATH,
            date_from=DATE_FROM,
            date_to=DATE_TO,
        )
    except pywintypes.com_error as e:
        hresult = e.args[0] if e.args else None
        if hresult == -2147418111:
            print(
                "拉取失败：Outlook 当前拒绝外部访问（Call was rejected by callee）。"
            )
            print("可能原因：Outlook 正在弹出对话框/卡死/未响应，请确认：")
            print("  - 正在使用经典桌面版 Outlook（不是“新 Outlook”）")
            print("  - Outlook 已正常打开且没有任何弹窗")
            print("  - 稍等几秒钟再重试脚本")
        else:
            print("拉取失败（COM 错误）：", e)
        sys.exit(2)
    except Exception as e:
        print("拉取失败：", e)
        sys.exit(2)

    if not texts:
        print("没有符合条件的邮件（主题需包含 feedback/survey）。")
        sys.exit(1)

    # 2) 生成报表
    df = build_report_from_texts(texts, REPORT_XLSX)
    rows = len(df)
    print(f"导出完成：{REPORT_XLSX}（{rows} 行）")

    # 3) 自检（导出）
    file_ok = (
        os.path.exists(REPORT_XLSX)
        and os.path.getsize(REPORT_XLSX) > 0
        and rows > 0
    )
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
    pythoncom.CoInitialize()
    try:
        main()
    finally:
        pythoncom.CoUninitialize()
