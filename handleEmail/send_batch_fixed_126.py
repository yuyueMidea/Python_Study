
"""
send_batch_fixed_126.py — 一键多封批量发送 + 失败重试 + 日志落盘 + 定时任务（1分钟/次）

使用说明
1) 在 126 邮箱后台开启 SMTP，并获取 “客户端授权码”。
2) 修改本文件 CONFIG 区域（发件人、授权码、收件人列表、主题模板等）。
3) 运行：python send_batch_fixed_126.py
   - RUN_MODE="once" 仅发送一轮
   - RUN_MODE="loop" 每隔 LOOP_INTERVAL_SECONDS 秒自动发送一次（默认 60 秒）

依赖
- 同目录下的 mailer.py（之前已提供）。本脚本基于 ReportMailer 与 SMTPConfig。

功能
- 固定配置（无需环境变量）
- 批量发送（一次发送多封，或“循环模式”每分钟发送一批测试数据）
- 失败自动重试（依赖 mailer.py 内置的指数退避重试）
- 日志落盘（rotating 文件日志 + 控制台）
"""
from __future__ import annotations
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import List, Dict, Any

from mailer import ReportMailer, SMTPConfig

# ===================== CONFIG（编辑这里）=====================
# 1) SMTP 账户（126 邮箱）
SMTP = SMTPConfig(
    host="smtp.126.com",
    port=465,                       # 465=SMTPS(SSL), 587=STARTTLS
    username="yy18825237023@126.com",
    password="",  # ← 必须是授权码，非登录密码
    use_tls=False,                  # 587→True / 465→False
    use_ssl=True,                   # 465→True / 587→False
)
FROM = "yy18825237023@126.com"     # 可写 "显示名 <邮箱>"

# 2) 批量收件人（可多组；每组都会独立发一封）
RECIPIENT_BATCH: List[Dict[str, Any]] = [
    # 每项为一封邮件的收件配置；可按需复制多份
    {"to": ["18825237023@163.com"], "cc": [], "bcc": []},
    {"to": ["yuyue920811@outlook.com"], "cc": [], "bcc": []},
    # {"to": ["another@example.com"], "cc": ["cc@example.com"], "bcc": []},
]

# 3) 主题与正文（可使用 {ts} 时间占位符）
SUBJECT_TEMPLATE = "【测试批量发送】{ts}"
TEXT_TEMPLATE = "这是一封批量测试邮件（纯文本）。时间：{ts}"
HTML_TEMPLATE = """
<div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; line-height:1.5">
  <h3 style="margin:0 0 8px">批量发送测试</h3>
  <p>当前时间：<b>{ts}</b></p>
  <p>这是一封 <b>HTML</b> 测试邮件 —— 来自自动化脚本。</p>
</div>
"""

# 4) 附件与内联图（按需）
ATTACHMENTS: List[str] = []  # 如 ["./report.csv"]
INLINE_IMAGES: Dict[str, str] = {}  # 如 {"logo": "./logo.png"}，HTML 用 <img src="cid:logo">

# 5) 重试/日志/循环策略
MAILER_MAX_RETRIES = 3            # mailer.py 内置重试次数
LOG_FILE = "send_batch.log"       # 日志文件名（自动滚动）
LOG_MAX_BYTES = 1 * 1024 * 1024   # 1MB
LOG_BACKUP_COUNT = 3
RUN_MODE = "loop"                 # "once" | "loop"
LOOP_INTERVAL_SECONDS = 60        # 循环模式下，每隔多少秒发送一批
MAX_LOOPS = 0                     # 0 = 无限循环；>0 = 循环次数上限
# =================== END CONFIG（编辑结束）===================


# -------------------- 日志初始化 --------------------
def setup_logger() -> logging.Logger:
    logger = logging.getLogger("batch_mailer")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # 控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # 文件（滚动）
    fh = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


# --------------------- 发送一封 ---------------------
def send_one(mailer: ReportMailer, rcpt_cfg: Dict[str, Any], logger: logging.Logger) -> bool:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = SUBJECT_TEMPLATE.format(ts=ts)
    text = TEXT_TEMPLATE.format(ts=ts)
    html = HTML_TEMPLATE.format(ts=ts)
    try:
        resp = mailer.send_report(
            subject=subject,
            to=rcpt_cfg.get("to", []),
            cc=rcpt_cfg.get("cc", []),
            bcc=rcpt_cfg.get("bcc", []),
            text=text,
            html=html,
            attachments=ATTACHMENTS,
            inline_images=INLINE_IMAGES,
        )
        logger.info(f"Sent OK → to={rcpt_cfg.get('to')} resp={resp}")
        return True
    except Exception as e:
        logger.error(f"Send FAIL → to={rcpt_cfg.get('to')} error={e}")
        return False


# --------------------- 发送一批 ---------------------
def send_batch(logger: logging.Logger) -> Dict[str, int]:
    mailer = ReportMailer(smtp=SMTP, from_addr=FROM, max_retries=MAILER_MAX_RETRIES)
    success = 0
    fail = 0
    for rcpt_cfg in RECIPIENT_BATCH:
        ok = send_one(mailer, rcpt_cfg, logger)
        success += 1 if ok else 0
        fail += 0 if ok else 1
    logger.info(f"Batch done. success={success}, fail={fail}")
    return {"success": success, "fail": fail}


# --------------------- 主流程 ---------------------
def main():
    logger = setup_logger()
    logger.info("---- Batch mailer started ----")
    logger.info(f"RUN_MODE={RUN_MODE}, LOOP_INTERVAL_SECONDS={LOOP_INTERVAL_SECONDS}, MAX_LOOPS={MAX_LOOPS}")

    if RUN_MODE == "once":
        send_batch(logger)
        logger.info("RUN_MODE=once finished.")
        return

    # 循环模式
    loops = 0
    while True:
        loops += 1
        logger.info(f"[Loop #{loops}] Start sending batch...")
        send_batch(logger)
        if MAX_LOOPS > 0 and loops >= MAX_LOOPS:
            logger.info(f"Reached MAX_LOOPS={MAX_LOOPS}. Exit.")
            break
        time.sleep(LOOP_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
