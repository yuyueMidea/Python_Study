# Outlook Feedback Export + Mail Sender 功能规格书 / Functional Specification Document

## 一、总体说明 / Overview
该脚本用于自动从本机 Outlook 客户端抓取指定邮件（如 Feedback、Survey 等），解析邮件内容生成结构化报表 (report.xlsx)，并自动将报表通过 Outlook 邮件发送到指定目标邮箱。系统在执行过程中会进行多项自检以确保每个阶段成功。

This script automatically retrieves feedback/survey emails from the local Outlook client, parses and exports the data into an Excel report (report.xlsx), and then sends the report to a specified recipient via Outlook. It includes built-in self-check mechanisms to ensure reliability throughout all steps.

---

## 二、系统环境要求 / System Requirements
**操作系统:** Windows 10 / 11  
**Outlook 客户端:** 已登录并可发送邮件的本机 Outlook  
**Python 版本:** 3.8+  
**依赖库:** pywin32, pandas, openpyxl  
**安装命令:** `pip install pywin32 pandas openpyxl`

**OS:** Windows 10 / 11  
**Outlook:** Installed and logged-in Outlook client  
**Python:** Version 3.8 or higher  
**Libraries:** pywin32, pandas, openpyxl  
**Install Command:** `pip install pywin32 pandas openpyxl`

---

## 三、主要功能 / Core Features
1. **抓取 Outlook 邮件 / Fetch Outlook Emails:** 使用 MAPI 接口读取邮件，支持按主题与发件人过滤。  
2. **解析 Feedback 文本 / Parse Feedback Text:** 提取 Ref ID、Q1–Q5 的分数与文字回答、提交日期与时间。  
3. **生成报表 / Generate Excel Report:** 输出 Excel 文件 report.xlsx。  
4. **自动发送报表 / Auto-send Report:** 将报表通过 Outlook 发送到指定邮箱。  
5. **自检机制 / Self-check System:** 检查导出与发送是否成功。

---

## 四、运行流程 / Process Flow
1. 初始化配置 / Load configuration  
2. 抓取 Outlook 邮件 / Fetch Outlook messages  
3. 解析正文 / Parse contents  
4. 生成 Excel 报表 / Generate report.xlsx  
5. 自检 #1 导出成功 / Run Self-check #1  
6. 发送报表邮件 / Send via Outlook  
7. 自检 #2 邮件发送验证 / Run Self-check #2  
8. 输出结果状态 / Display summary

---

## 五、配置参数 / Configuration Parameters
| 参数 / Parameter | 默认值 / Default | 说明 / Description |
|------------------|------------------|--------------------|
| OUTLOOK_FOLDER_PATH | Inbox | 邮件路径 / Folder path |
| SHOW_LIMIT | 500 | 最多读取邮件数 / Max messages |
| SUBJECT_KEYWORDS | feedback, survey | 主题过滤词 / Subject keywords |
| SURVEY_SENDERS | [] | 发件人白名单 / Sender whitelist |
| REPORT_XLSX | report.xlsx | 输出文件名 / Output filename |
| TARGET_TO | someone@example.com | 收件人 / Recipient |
| MAIL_SUBJECT_PREFIX | Feedback Report | 邮件主题前缀 / Subject prefix |
| SENT_CHECK_TIMEOUT | 45 | 验证超时（秒） / Timeout (seconds) |

---

## 六、输出文件 / Output Description
- **文件 / File:** `report.xlsx`  
- **说明 / Description:** 包含 Ref ID, Q1–Q5 Score/Text, Submit Date, Submit Time.

---

## 七、日志与结果 / Logging & Results
脚本输出匹配邮件数、生成行数、自检结果 (PASS/FAIL) 及最终状态。  
Displays mail count, exported rows, self-check results (PASS/FAIL), and overall status.

---

## 八、异常处理 / Error Handling
| 场景 / Scenario | 系统反应 / Behavior |
|-----------------|--------------------|
| Outlook 未登录 / Outlook not logged in | 抛出异常 / Raises exception |
| 无匹配邮件 / No matching emails | 提示后退出 / Displays message and exits |
| 导出失败 / Export failure | 自检失败 / Self-check fail |
| 发送失败 / Send failure | 提示错误 / Shows error |
| 验证超时 / Verification timeout | 邮件验证失败 / Delivery check fail |

---

## 九、使用说明 / User Guide
1. 安装依赖 / Install dependencies  
   ```bash
   pip install pywin32 pandas openpyxl
   ```
2. 修改脚本配置 / Edit configuration  
3. 运行脚本 / Run script  
   ```bash
   python outlook_feedback_export.py
   ```
4. 程序生成并发送报表 / Script generates and sends report.

---

## 十、维护与扩展 / Maintenance & Extension
可扩展过滤逻辑、输出格式或使用 SMTP 发送。  
Extend filters, output formats, or replace Outlook MAPI with SMTP.
