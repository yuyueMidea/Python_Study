
"""
send_fixed_126.py — One-file sender with all config hardcoded for quick testing.

HOW TO USE
1) 在 126 邮箱后台开启 SMTP，并获取 “客户端授权码”。
2) 修改下面 CONFIG 区域中的 USERNAME / PASSWORD / TO / SUBJECT / TEXT / HTML 等字段。
3) 运行：python send_fixed_126.py
4) 控制台看到 "Send status: OK" 代表发信端成功提交。
"""
from __future__ import annotations
from mailer import ReportMailer, SMTPConfig

# ===================== CONFIG (编辑这里) =====================
SMTP = SMTPConfig(
    host="smtp.126.com",
    port=465,            # 465=SMTPS(SSL), 587=STARTTLS
    username="yy18825237023@126.com",
    password="",  # ← 必须是授权码，非登录密码
    use_tls=False,       # 587→True / 465→False
    use_ssl=True,        # 465→True / 587→False
)

FROM = "yy18825237023@126.com"  # 可写成 "显示名 <邮箱>" 格式
TO = ["18825237023@163.com"]    # 目标收件人，可填多个
CC = []                         # 抄送
BCC = []                        # 密送

SUBJECT = "Hello from 126 (fixed config)"

# 纯文本正文（可留空）
TEXT = "这是一封来自 126 SMTP 的测试邮件（纯文本正文）。"

# 富文本正文（可留空）
HTML = """
<div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; line-height:1.5">
  <h2 style="margin:0 0 8px">测试：126 邮件发送</h2>
  <p>这是一封 <b>HTML</b> 富文本测试邮件。</p>
  <ul>
    <li>支持纯文本 + HTML</li>
    <li>支持附件、CC/BCC、内联图片</li>
  </ul>
  <p>—— 自动化测试脚本</p>
</div>
"""

# 附件（可选）：填写本机文件路径，如 ["./report.csv"]
ATTACHMENTS = []

# 内联图片（可选）：用于 <img src="cid:logo"> 这样的引用
INLINE_IMAGES = {
    # "logo": "./logo.png"
}
# =================== END CONFIG (编辑结束) ===================


def main():
    mailer = ReportMailer(smtp=SMTP, from_addr=FROM)
    resp = mailer.send_report(
        subject=SUBJECT,
        to=TO,
        cc=CC,
        bcc=BCC,
        text=TEXT,
        html=HTML,
        attachments=ATTACHMENTS,
        inline_images=INLINE_IMAGES,
    )
    print("Send status:", resp)

if __name__ == "__main__":
    main()
