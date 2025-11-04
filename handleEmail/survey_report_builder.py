import re
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import pandas as pd

# ========= 可配置 =========
OUTPUT_XLSX = "report.xlsx"

# 你要求的列顺序（严格按此导出）
REPORT_COLUMNS = [
    "Ref ID",
    "Q1 Score", "Q1 Text",
    "Q2 Score", "Q2 Text",
    "Q3 Score", "Q3 Text",
    "Q4 Score", "Q4 Text",
    "Q5 Score", "Q5 Text",
    "Submit Date", "Submit Time"
]

# ========= 正则与解析工具 =========

# 例：eFrom submit date: 25/06/2025 - 11:52
RE_SUBMIT = re.compile(
    r"submit\s*date\s*:\s*(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*[-–—]\s*(?P<time>\d{1,2}:\d{2})",
    re.IGNORECASE
)

# 例：Ref ID: UMD00089xxx
RE_REFID = re.compile(r"ref\s*id\s*[:#-]?\s*(?P<id>[A-Za-z0-9_-]+)", re.IGNORECASE)

# 例：1a:5、1b:xxx（允许 1) 1. 1- 等分隔符；容错空格）
RE_QA = re.compile(
    r"^(?:Q\s*)?(?P<num>[1-5])\s*(?P<sub>[ab])\s*[:\-\)\.]\s*(?P<val>.+?)\s*$",
    re.IGNORECASE
)

def _parse_submit(line: str) -> Optional[Tuple[str, str]]:
    m = RE_SUBMIT.search(line)
    if not m:
        return None
    raw_date = m.group("date").strip()
    raw_time = m.group("time").strip()

    # 统一日期为 dd/mm/yyyy，时间为 HH:MM（不加秒）
    # 自动纠正两位年份
    # 允许分隔符 / 或 -
    day, month, year = re.split(r"[/-]", raw_date)
    if len(year) == 2:
        year = "20" + year  # 粗略推断 20xx
    # 规范化：补零
    day = day.zfill(2)
    month = month.zfill(2)
    if len(year) == 3:  # 极端容错
        year = year.zfill(4)

    # 校验日期合法性（不合法则原样返回）
    try:
        _ = datetime(int(year), int(month), int(day))
        std_date = f"{day}/{month}/{year}"
    except ValueError:
        std_date = raw_date

    # 规范化时间
    hh, mm = raw_time.split(":")
    std_time = f"{hh.zfill(2)}:{mm.zfill(2)}"

    return std_date, std_time


def _parse_refid(text: str) -> Optional[str]:
    m = RE_REFID.search(text)
    return m.group("id").strip() if m else None


def _parse_answers(text: str) -> Dict[str, str]:
    """
    抽取 1a..5b；返回 dict，如 {'1a':'5','1b':'xxx',...}
    """
    answers: Dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = RE_QA.match(line)
        if m:
            k = f"{m.group('num').lower()}{m.group('sub').lower()}"
            v = m.group("val").strip()
            answers[k] = v
    return answers


def parse_single_email_body(body: str) -> Dict[str, str]:
    """
    输入一封邮件的纯文本正文，返回一行记录（符合 REPORT_COLUMNS）
    缺失项会填空串 ""。
    """
    # 先整体提取 ref / submit（允许在任意行）
    ref_id = _parse_refid(body) or ""
    submit_dt = _parse_submit(body) or ("", "")
    submit_date, submit_time = submit_dt

    # 再逐行抓题目
    answers = _parse_answers(body)

    # 组装一行（映射：a=Score，b=Text）
    row = {
        "Ref ID": ref_id,
        "Q1 Score": answers.get("1a", ""),
        "Q1 Text":  answers.get("1b", ""),
        "Q2 Score": answers.get("2a", ""),
        "Q2 Text":  answers.get("2b", ""),
        "Q3 Score": answers.get("3a", ""),
        "Q3 Text":  answers.get("3b", ""),
        "Q4 Score": answers.get("4a", ""),
        "Q4 Text":  answers.get("4b", ""),
        "Q5 Score": answers.get("5a", ""),
        "Q5 Text":  answers.get("5b", ""),
        "Submit Date": submit_date,
        "Submit Time": submit_time,
    }
    return row


# ========= 主函数：多封正文 → DataFrame → XLSX =========

def build_report_from_texts(texts: List[str], out_xlsx: str = OUTPUT_XLSX) -> pd.DataFrame:
    """
    :param texts: 多封邮件的纯文本正文（你先用自己的读取器把HTML转纯文本）
    :param out_xlsx: 输出路径
    :return: 构建好的 DataFrame（列顺序固定）
    """
    rows = []
    for body in texts:
        try:
            rows.append(parse_single_email_body(body))
        except Exception:
            # 单封解析失败时，仍然写一行仅含 Ref ID 与 Submit 字段（若能抓到）
            ref_id = _parse_refid(body) or ""
            dt = _parse_submit(body) or ("", "")
            rows.append({
                "Ref ID": ref_id,
                "Q1 Score": "", "Q1 Text": "",
                "Q2 Score": "", "Q2 Text": "",
                "Q3 Score": "", "Q3 Text": "",
                "Q4 Score": "", "Q4 Text": "",
                "Q5 Score": "", "Q5 Text": "",
                "Submit Date": dt[0], "Submit Time": dt[1],
            })

    df = pd.DataFrame(rows, columns=REPORT_COLUMNS)

    # —— 去重逻辑（可按需调整）——
    # 用 (Ref ID, Submit Date, Submit Time) 去重，保留第一次出现
    df = df.drop_duplicates(subset=["Ref ID", "Submit Date", "Submit Time"], keep="first")

    # —— 可选：把评分列转为数值型（便于后续统计）——
    for col in ["Q1 Score", "Q2 Score", "Q3 Score", "Q4 Score", "Q5 Score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 导出 Excel
    os.makedirs(os.path.dirname(out_xlsx) or ".", exist_ok=True)
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Survey")

    return df


# ========= 示例用法（可直接运行做自检） =========
if __name__ == "__main__":
    sample = """
eFrom submit date: 25/06/2025 - 11:52
Ref ID: UMD00089xxx
1a:5
1b:xxx1
2a:5
2b:xxx
3a:4
3b:xxx
4a:4
4b:xxx
5a:4
5b:xxx
    """.strip()

    df = build_report_from_texts([sample], out_xlsx=OUTPUT_XLSX)
    print(df)
    print(f"Saved to {OUTPUT_XLSX}")
