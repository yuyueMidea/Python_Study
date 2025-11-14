# scheduler_wrapper.py
from apscheduler.schedulers.blocking import BlockingScheduler
import pythoncom
import logging
from datetime import datetime

# 直接复用你现有脚本里的 main
from fetch_feedback_and_send import main as run_outlook_job


logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def job():
    """真正执行一次“抓取+导出+发邮件”的 Job。"""
    logger.info("Job started")
    pythoncom.CoInitialize()
    try:
        run_outlook_job()
        logger.info("Job finished")
    except Exception:
        logger.exception("Job failed")
    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    # 方案 A：每天两次，比如 09:00 和 18:00
    scheduler.add_job(
        job,
        "cron",
        hour=[9, 18],
        minute=0,
        id="feedback_twice_daily",
        max_instances=1,      # 避免上一个没跑完又进来了
        coalesce=True,        # 如果错过执行时间，合并为一次
        misfire_grace_time=3600,  # 最多允许延迟 1 小时
    )

    # 方案 B：每 X 小时一次（例如每 4 小时）
    # scheduler.add_job(
    #     job,
    #     "interval",
    #     hours=4,
    #     id="feedback_every_4h",
    #     max_instances=1,
    # )

    try:
        logger.info("Scheduler started")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
