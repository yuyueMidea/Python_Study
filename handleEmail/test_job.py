#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime

logging.basicConfig(
    filename="job.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def main():
    logging.info("Job started")
    try:
        # TODO: 在这里写你的业务逻辑，比如拉取邮件、生成报表
        logging.info("Doing work...")
    except Exception as e:
        logging.exception("Job failed")
    else:
        logging.info("Job finished successfully")

if __name__ == "__main__":
    main()
