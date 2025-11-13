# fetch_feedback_and_send.py Technical Specification / 技术规格书

---

## Part A – Chinese Specification / 中文规格书

### 1. 文档信息

- **脚本名称**：`fetch_feedback_and_send.py`
- **版本号**：v1.0.0
- **发布日期**：2025-11-13
- **作者**：自动生成（ChatGPT）
- **适用场景**：Windows 桌面环境，使用本机 Outlook 客户端收集问卷反馈，生成 Excel 报表并通过 Outlook 自动发送。

### 2. 概述

#### 2.1 目标

该脚本用于在本机自动化完成以下流程：

1. 通过 `pywin32` 调用本机 Outlook，按时间、主题、发件人等条件抓取邮件；
2. 从邮件正文中解析问卷反馈内容；
3. 生成标准结构的 Excel 报表文件 `report.xlsx`；
4. 使用本机 Outlook 创建并发送带有报表附件的邮件至指定收件人；
5. 在“已发送邮件”中回查一次性 Token，确认邮件已经成功发送（自检）。

#### 2.2 功能范围

- 支持按日期范围过滤邮件（`DATE_FROM` / `DATE_TO`）；
- 支持按主题关键词、发件人白名单过滤问卷邮件；
- 支持解析问卷中 Q1–Q5（评分 + 文本）以及 Ref ID、提交时间；
- 将解析结果导出为固定列结构的 Excel 文件；
- 自动构造带唯一 Token 的邮件主题并通过 Outlook 发送；
- 在指定时间窗口内轮询“已发送邮件”文件夹，确认是否存在含 Token 的邮件。

#### 2.3 不在范围

- 不负责在服务器端运行（依赖本机 Outlook 客户端）；
- 不管理 IMAP/POP3/Exchange 账户配置；
- 不保证支持“新 Outlook”（Web/Preview 版），只针对经典桌面版 Outlook。

---

### 3. 系统环境与依赖

#### 3.1 硬件与操作系统

- 操作系统：Windows 10 或以上版本（必须支持 COM / MAPI）
- CPU/内存：无特别要求，建议 ≥4GB 内存

#### 3.2 软件与工具

- 本机已安装并登录的 **经典桌面版 Outlook**（非“新 Outlook”）
- Python 版本：3.8+（建议 3.9 或以上）
- 已安装并可用的 Office MAPI 组件

#### 3.3 Python 依赖包

- 标准库：`os`, `re`, `sys`, `time`, `uuid`, `datetime`, `typing`, `logging`
- 第三方库：
  - `pandas`
  - `pywin32`（`win32com.client`）
  - `pywintypes`（随 pywin32 提供）
  - `pythoncom`（随 pywin32 提供）

安装示例：

```bash
pip install pandas pywin32
```

---

### 4. 高层架构与处理流程

#### 4.1 总体流程（逻辑步骤）

1. 初始化 COM（`pythoncom.CoInitialize()`）；
2. 调用 `main()`：
   1. 通过 `fetch_outlook_messages()` 按配置抓取 Outlook 邮件文本；
   2. 调用 `build_report_from_texts()` 将文本解析为结构化数据并导出为 Excel；
   3. 自检导出结果（文件存在、非空且有数据行）；
   4. 调用 `send_report_via_outlook()` 发送带附件的报告邮件；
   5. 调用 `wait_sent_verification()` 在“已发送邮件”中查找包含 Token 的邮件，自检发送结果；
   6. 根据自检情况输出 Overall: PASS / PARTIAL 并返回退出码。

#### 4.2 模块划分

- **配置模块**：脚本顶部常量配置（文件夹路径、时间范围、主题关键字、收件人等）；
- **文本解析模块**：解析问卷正文、识别 Ref ID、Q1–Q5 及提交时间；
- **Outlook 访问模块**：封装 COM 调用与重试策略，安全访问 Outlook；
- **报表导出模块**：将解析后的数据写入 Excel；
- **邮件发送模块**：构造带 Token 的主题，创建 Outlook 邮件并发送；
- **自检模块**：检查 Excel 文件与“已发送邮件”记录，给出结果。

---

### 5. 配置项说明

#### 5.1 主要配置常量

| 变量名                  | 类型           | 默认值                           | 说明 |
|-------------------------|----------------|----------------------------------|------|
| `OUTLOOK_FOLDER_PATH`   | `str`          | `"Inbox"`                        | 要抓取的 Outlook 文件夹路径，支持 `"Inbox"` 或 `"Inbox\Sub1\Sub2"` |
| `SHOW_LIMIT`            | `int`          | `500`                            | 最大处理的邮件数，从最近往前数 |
| `DATE_FROM`             | `str`          | `"2025-11-06"`                   | 起始日期（含），支持 `YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM` |
| `DATE_TO`               | `str`          | `"2025-11-06"`                   | 结束日期（含） |
| `SUBJECT_KEYWORDS`      | `List[str]`    | `["feedback", "survey"]`         | 主题包含的关键词（小写匹配） |
| `SURVEY_SENDERS`        | `List[str]`    | `[]`                             | 发件人白名单，尾部匹配（如 `"@example.com"`） |
| `REPORT_XLSX`           | `str`          | `"report.xlsx"`                  | 导出的 Excel 文件名 |
| `TARGET_TO`             | `List[str]`    | `["someone@example.com"]`        | 发送报表的收件人列表 |
| `TARGET_CC`             | `List[str]`    | `[]`                             | 抄送列表 |
| `TARGET_BCC`            | `List[str]`    | `[]`                             | 密送列表 |
| `MAIL_SUBJECT_PREFIX`   | `str`          | `"[Feedback Report]"`            | 邮件主题前缀，后附加 Token |
| `MAIL_BODY_TEXT`        | `str`          | 固定正文                         | 邮件正文内容 |
| `SENT_CHECK_TIMEOUT`    | `int`          | `45`                             | 在“已发送邮件”中查找的最大秒数 |
| `SENT_CHECK_INTERVAL`   | `int`          | `3`                              | 每次轮询间隔秒数 |

#### 5.2 Excel 列结构

`REPORT_COLUMNS` 定义了导出的字段顺序：

1. `Ref ID`
2. `Q1 Score`
3. `Q1 Text`
4. `Q2 Score`
5. `Q2 Text`
6. `Q3 Score`
7. `Q3 Text`
8. `Q4 Score`
9. `Q4 Text`
10. `Q5 Score`
11. `Q5 Text`
12. `Submit Date`
13. `Submit Time`

---

### 6. 核心函数说明

以下为关键函数的用途概要（不列出全部代码实现细节）：

#### 6.1 文本解析相关

- `_strip_html(html: str) -> str`  
  去除 HTML 标签并压缩空白，输出纯文本。

- `_parse_refid(text: str) -> str`  
  利用正则 `Ref ID` 或 `Reference ID` 提取问卷的唯一标识。

- `_parse_submit_block(text: str) -> (str, str)`  
  从文本中解析提交日期与时间，输出为标准化的 `dd/mm/yyyy` 和 `HH:MM`。

- `_parse_answers(text: str) -> Dict[str, str>`  
  解析 Q1–Q5 中的评分与文本回答，例如 `1a` 表示 Q1 Score，`1b` 表示 Q1 Text。

- `parse_single_body(body: str) -> Dict[str, str>`  
  综合调用上述函数，从一封邮件正文中抽取完整的问卷结构信息。

#### 6.2 Outlook COM 调用与重试

- `safe_com_call(func, *args, retries=3, delay=1.0, **kwargs)`  
  为任意 COM 调用增加重试逻辑，重点处理 `RPC_E_CALL_REJECTED (-2147418111)`，避免 Outlook 忙碌导致随机失败。

- `create_outlook_instance(max_retries=3, retry_delay=2.0)`  
  使用 `Dispatch` / `EnsureDispatch` / `dynamic.Dispatch` 等多种方式尝试连接 Outlook，并结合 `safe_com_call` 实现稳健的连接重试。

- `_resolve_folder(namespace, folder_path: str)`  
  根据配置的路径字符串找到对应邮箱文件夹，支持子文件夹路径。

#### 6.3 邮件抓取与过滤

- `fetch_outlook_messages(...) -> List[str]`  
  核心功能：按时间、发件人、主题、正文关键词等多维条件，从指定 Outlook 文件夹中抓取邮件正文列表。  
  关键点：
  - 使用 `Items.Sort("[ReceivedTime]", True)` 按时间倒序；
  - 优先尝试使用 `Items.Restrict()` 在 MAPI 端做时间过滤；
  - 对每封邮件通过 `restricted.Item(index)` 访问，并用 `safe_com_call` 包裹，单封失败不会终止整个流程；
  - 对主题关键字、发件人、正文关键字做 Python 侧过滤。

#### 6.4 报表导出

- `build_report_from_texts(texts: List[str], out_xlsx: str) -> pd.DataFrame`  
  对每封邮件正文调用 `parse_single_body()`，将结果整理为 `pandas.DataFrame`，并写出为 Excel 文件。

#### 6.5 邮件发送与自检

- `send_report_via_outlook(report_path, to, cc, bcc, subject_prefix, body_text) -> (str, str)`  
  通过 Outlook 创建一封带附件的邮件：
  - 生成一次性 Token（UUID 前 8 位）；
  - 主题为 `subject_prefix + " [token]"`；
  - 将 Excel 报表作为附件添加；
  - 调用 `mail.Send()` 发送；
  - 返回 `(subject, token)`。

- `wait_sent_verification(token: str) -> bool`  
  在超时时间内轮询“已发送邮件”文件夹，是否存在主题包含该 Token 的邮件，作为发送成功的自检依据。

---

### 7. 错误处理与退出码

#### 7.1 错误处理策略

- 所有关键 COM 调用通过 `safe_com_call` 增加重试；
- 对 `pywintypes.com_error` 进行专门捕获，识别 `Call was rejected by callee` 并提示用户检查 Outlook 状态；
- 单封邮件处理失败会被记录警告并跳过，不影响整体运行。

#### 7.2 退出码定义

- `0`：全部流程成功（抓取、导出、发送、自检均通过）；
- `1`：未找到符合条件的邮件；
- `2`：抓取阶段出现错误（包括 COM 错误）；
- `3`：报表导出失败或结果无数据；
- `4`：邮件发送失败；
- `5`：报表导出成功但发送自检失败（部分成功）。

---

### 8. 安全与隐私

- 所有数据均在本机处理，不上传至外部服务器；
- 报表中包含问卷内容及可能的个人信息，应按公司数据保护规范进行存储和传输；
- 建议对生成的报表文件和脚本运行环境设置访问控制；
- 不在脚本中硬编码敏感邮箱地址或密码（发送依赖 Outlook 当前登录身份）。

---

### 9. 部署与运行步骤

1. 安装 Python、pandas、pywin32；
2. 安装并配置经典桌面版 Outlook，确认能正常收发邮件；
3. 将脚本 `fetch_feedback_and_send.py` 放置于任意工作目录；
4. 根据实际需求修改脚本顶部的配置项（时间范围、主题关键词、收件人等）；
5. 在命令行进入脚本目录，运行：

   ```bash
   python fetch_feedback_and_send.py
   ```

6. 观察终端输出：
   - 确认显示 `导出完成：report.xlsx（N 行）`；
   - 自检结果 `Self-check[Export]: PASS` 和 `Self-check[Mail Sent]: PASS`；
   - Overall 显示 `PASS` 则表示流程全部成功。

---

### 10. 已知限制与扩展方向

- 对“新 Outlook”（UWP/Web 版）的支持不保证；
- 邮件正文解析基于约定格式（Ref ID、Q1–Q5 等），若格式变动需更新正则；
- 当前只处理 Q1–Q5，可扩展支持更多问题；
- 可扩展为命令行参数传入时间范围、输出路径等，以便整合进 CI/定时任务。

---

## Part B – English Specification

### 1. Document Information

- **Script Name**: `fetch_feedback_and_send.py`
- **Version**: v1.0.0
- **Release Date**: 2025-11-13
- **Author**: Auto-generated (ChatGPT)
- **Use Case**: Run on a Windows desktop with Outlook installed to collect survey feedback emails, generate an Excel report, and send it automatically via Outlook.

### 2. Overview

#### 2.1 Objective

This script automates the following workflow on a local machine:

1. Use `pywin32` to connect to the local Outlook client and fetch emails by time range, subject, and sender;
2. Parse survey content from email bodies;
3. Generate a structured Excel report `report.xlsx`;
4. Send the report as an email attachment via Outlook to configured recipients;
5. Look up a one-time token in the “Sent Items” folder to confirm the email was successfully sent (self-check).

#### 2.2 Scope

- Filter emails by date range (`DATE_FROM` / `DATE_TO`);
- Filter survey emails by subject keywords and sender whitelist;
- Parse Q1–Q5 (score + text), Ref ID, and submission time from survey emails;
- Export parsed data into a fixed-column Excel file;
- Construct an email subject containing a unique token and send via Outlook;
- Poll the “Sent Items” folder within a time window to verify a message containing the token was sent.

#### 2.3 Out of Scope

- Server-side or headless execution (depends on local Outlook client);
- Managing IMAP/POP3/Exchange account configurations;
- Supporting “New Outlook” (web/preview); only classic desktop Outlook is targeted.

---

### 3. Environment and Dependencies

#### 3.1 OS & Hardware

- OS: Windows 10 or later (COM / MAPI support required)
- Hardware: no special requirements; ≥4GB RAM recommended

#### 3.2 Software

- Classic desktop Outlook client (not “New Outlook”)
- Python 3.8+ (3.9+ recommended)
- Office MAPI components installed and working

#### 3.3 Python Packages

- Standard library: `os`, `re`, `sys`, `time`, `uuid`, `datetime`, `typing`, `logging`
- Third-party:
  - `pandas`
  - `pywin32` (`win32com.client`)
  - `pywintypes` and `pythoncom` (bundled with pywin32)

Example installation:

```bash
pip install pandas pywin32
```

---

### 4. High-Level Architecture & Flow

#### 4.1 End-to-End Flow

1. Initialize COM (`pythoncom.CoInitialize()`).
2. Call `main()`:
   1. Fetch email bodies via `fetch_outlook_messages()` according to configuration;
   2. Convert them to structured rows and export to Excel using `build_report_from_texts()`; 
   3. Self-check the export result (file existence, non-empty, row count > 0);
   4. Send the report as an attachment via `send_report_via_outlook()`; 
   5. Run `wait_sent_verification()` to search “Sent Items” for a message containing the generated token;
   6. Print Overall: PASS / PARTIAL and exit with an appropriate status code.

#### 4.2 Module Breakdown

- **Configuration**: top-level constants for folder path, time range, subject keywords, recipients, etc.
- **Text Parsing**: parse survey bodies, extract Ref ID, Q1–Q5 answers, and submission timestamps.
- **Outlook Access**: encapsulate COM calls and retry logic for stable access.
- **Report Export**: write parsed data into an Excel file.
- **Email Sending**: build a tokenized subject, create an Outlook email, and send it.
- **Self-check**: verify report export and that the email appears in “Sent Items”.

---

### 5. Configuration

#### 5.1 Main Constants

See the Chinese section’s table for all configuration constants. They have the same semantics:

- `OUTLOOK_FOLDER_PATH`: Outlook folder path (supports subfolders).
- `SHOW_LIMIT`: max number of emails to process.
- `DATE_FROM` / `DATE_TO`: date/time range for filtering.
- `SUBJECT_KEYWORDS`: subject keywords to match survey emails.
- `SURVEY_SENDERS`: sender whitelist (suffix match).
- `REPORT_XLSX`: Excel output file name.
- `TARGET_TO`, `TARGET_CC`, `TARGET_BCC`: recipient lists.
- `MAIL_SUBJECT_PREFIX`: email subject prefix.
- `MAIL_BODY_TEXT`: email body template.
- `SENT_CHECK_TIMEOUT`, `SENT_CHECK_INTERVAL`: self-check timing.

#### 5.2 Excel Schema

The Excel file contains the following columns in order:

1. `Ref ID`
2. `Q1 Score`
3. `Q1 Text`
4. `Q2 Score`
5. `Q2 Text`
6. `Q3 Score`
7. `Q3 Text`
8. `Q4 Score`
9. `Q4 Text`
10. `Q5 Score`
11. `Q5 Text`
12. `Submit Date`
13. `Submit Time`

---

### 6. Core Functions

#### 6.1 Parsing

- `_strip_html(html: str) -> str`  
  Remove HTML tags and normalize whitespace.

- `_parse_refid(text: str) -> str`  
  Extract the unique survey ID (`Ref ID` / `Reference ID`) via regex.

- `_parse_submit_block(text: str) -> (str, str)`  
  Parse the submission date and time; normalize to `dd/mm/yyyy` and `HH:MM`.

- `_parse_answers(text: str) -> Dict[str, str>`  
  Parse Q1–Q5 answers (score/text) from the body; keys like `1a`, `1b` represent score/text pairs.

- `parse_single_body(body: str) -> Dict[str, str>`  
  Combine all parsing steps into a single structured record for one email body.

#### 6.2 Outlook COM & Retry

- `safe_com_call(func, *args, retries=3, delay=1.0, **kwargs)`  
  Wrap a COM call with retry logic, focusing on `RPC_E_CALL_REJECTED` (“Call was rejected by callee”).

- `create_outlook_instance(max_retries=3, retry_delay=2.0)`  
  Try various ways (`Dispatch`, `EnsureDispatch`, `dynamic.Dispatch`) to connect to Outlook, with retries via `safe_com_call`.

- `_resolve_folder(namespace, folder_path: str)`  
  Resolve an Outlook folder from a path string like `"Inbox\Sub1\Sub2"`.

#### 6.3 Fetching & Filtering Emails

- `fetch_outlook_messages(...) -> List[str]`  
  Fetch email bodies from a given folder with multi-dimensional filtering:
  - Sort by received time descending;
  - Optionally use `Items.Restrict()` for date-range filtering;
  - For each item, access via `restricted.Item(index)` and wrap with `safe_com_call`;
  - Apply sender, subject, and body keyword filters in Python.

#### 6.4 Report Export

- `build_report_from_texts(texts, out_xlsx) -> pd.DataFrame`  
  Parse each email body, construct a `DataFrame`, and write it as an Excel file.

#### 6.5 Sending & Verification

- `send_report_via_outlook(report_path, to, cc, bcc, subject_prefix, body_text) -> (str, str)`  
  Create and send an Outlook email with the report attached; generate a short token and include it in the subject.

- `wait_sent_verification(token: str) -> bool`  
  Poll the “Sent Items” folder within a configurable timeout to verify that a message containing the token appears.

---

### 7. Error Handling & Exit Codes

#### 7.1 Strategy

- Use `safe_com_call` for robust COM calls with retries.
- Catch `pywintypes.com_error`, detect `Call was rejected by callee`, and print user-friendly hints (e.g., Outlook busy, pop-ups).
- Skip individual emails that fail to load instead of failing the entire run.

#### 7.2 Exit Codes

- `0`: Success (fetch, export, send, self-check all passed).
- `1`: No matching emails found.
- `2`: Error during fetching (including COM errors).
- `3`: Report export failed or produced no rows.
- `4`: Email sending failed.
- `5`: Export succeeded, but send verification failed (partial success).

---

### 8. Security & Privacy

- All data is processed locally; nothing is sent to external servers by the script itself.
- The report may contain sensitive survey content or personal data; handle according to your organization's data protection policy.
- Protect access to the script and generated reports (file permissions, encryption if necessary).
- No passwords or sensitive account details are stored in the script; sending uses the existing Outlook session.

---

### 9. Deployment & Usage

1. Install required software (Python, Outlook) and packages (`pandas`, `pywin32`).
2. Ensure classic desktop Outlook is installed and configured to send/receive.
3. Place `fetch_feedback_and_send.py` in a working directory.
4. Edit configuration constants at the top of the script to match your environment.
5. Run the script:

   ```bash
   python fetch_feedback_and_send.py
   ```

6. Check console output:
   - Confirm the message `导出完成：report.xlsx（N 行）` / `Export completed: report.xlsx (N rows)` appears;
   - Ensure both `Self-check[Export]: PASS` and `Self-check[Mail Sent]: PASS` are printed;
   - Overall `PASS` indicates a fully successful run.

---

### 10. Limitations & Future Enhancements

- No guarantee for “New Outlook” (UWP/web) compatibility.
- Parsing logic assumes a specific survey format (Ref ID, Q1–Q5); update regexes if the format changes.
- Currently hard-coded for Q1–Q5; can be extended to support more questions.
- Can be enhanced to accept CLI parameters for time range, output path, and configuration profile.
