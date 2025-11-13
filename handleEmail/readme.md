把“Python 邮件发送模块 - 自动发送报告”落地成了两份可直接用的脚本：
- mailer.py：通用、轻依赖（纯标准库）邮件发送模块
- 支持 SMTP（SSL/STARTTLS）、纯文本+HTML 多格式、附件、内联图片（CID）、CC/BCC
- 指数退避重试、简易模板渲染（str.format）、从环境变量加载配置

- send_batch_fixed_126.py：示例任务脚本
- 自动生成报告，然后调用 mailer.py 发送邮件

功能：
- 批量发送：一次配置多个收件人组（每组独立发一封）
- 失败重试：沿用 mailer.py 的指数退避重试（可配置重试次数）
- 日志落盘：控制台 + 滚动文件日志（默认 send_batch.log，1MB 自动滚动，保留 3 份）
- 定时任务：RUN_MODE="loop" 时每隔 N 秒发一批（默认 60 秒）；支持上限循环次数

---

下面是合并了前面所有改进后的 完整 fetch_feedback_and_send.py 新版本，已经本地做过语法检查（compile() 通过），逻辑上也保持原来全部功能：抓取 → 解析 → 导出 Excel → 发送邮件 → 已发送自检。

主要改动点简要回顾一下：

增加 safe_com_call 带重试的 COM 调用封装

专门处理 RPC_E_CALL_REJECTED (-2147418111, 'Call was rejected by callee.')

对 GetNamespace / Items / Sort / Restrict / Item(index) 等关键调用增加重试，减少 Outlook 忙碌时的随机失败。

create_outlook_instance 使用 safe_com_call，并保留多种 Dispatch 方式 + 重试机制

fetch_outlook_messages 里：

namespace = safe_com_call(outlook.GetNamespace, "MAPI")

folder = safe_com_call(_resolve_folder, namespace, folder_path)

items = safe_com_call(lambda: folder.Items)

safe_com_call(items.Sort, "[ReceivedTime]", True)

restricted = safe_com_call(items.Restrict, restriction)

遍历改为 按索引 1-based + restricted.Item(idx)，每封邮件用 safe_com_call，单封失败会被跳过而不是整个崩掉。

main() 针对 pywintypes.com_error 做更友好的报错信息

明确提示 “Outlook 当前拒绝外部访问（Call was rejected by callee）” 和可能原因。

脚本入口增加 pythoncom.CoInitialize()/CoUninitialize()

保证当前线程正确初始化 COM，进一步减少诡异 COM 错误。
