
"""
mailer.py — Lightweight, robust email sending module for automated reports.

Features:
  - SMTP with TLS/SSL
  - Plaintext + HTML (multipart/alternative)
  - Attachments (any filetype, MIME guessed)
  - Inline images (CID)
  - CC / BCC
  - Retry with exponential backoff
  - Simple templating via str.format / string.Template
  - Minimal deps: standard library only

Env-vars (optional):
  SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM, SMTP_USE_SSL, SMTP_USE_TLS
Usage:
  from mailer import ReportMailer
  mailer = ReportMailer.from_env()
  mailer.send_report(subject="Daily Report", to=["me@acme.com"], html="<b>Hello</b>")
"""
from __future__ import annotations
import os
import ssl
import time
import mimetypes
from dataclasses import dataclass, field
from email.message import EmailMessage
from email.utils import make_msgid, formatdate
from email.headerregistry import Address
import smtplib
from pathlib import Path
from typing import Iterable, List, Optional, Dict, Any, Union, Tuple

AddressLike = Union[str, Address]

def _coerce_recipients(x: Optional[Union[AddressLike, Iterable[AddressLike]]]) -> List[str]:
    if x is None:
        return []
    if isinstance(x, (str, Address)):
        return [str(x)]
    return [str(i) for i in x]

def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

@dataclass
class SMTPConfig:
    host: str
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True     # STARTTLS
    use_ssl: bool = False    # SMTPS on 465
    timeout: float = 30.0

    @staticmethod
    def from_env() -> "SMTPConfig":
        host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        port = int(os.getenv("SMTP_PORT", "587"))
        username = os.getenv("SMTP_USERNAME")
        password = os.getenv("SMTP_PASSWORD")
        use_ssl = _bool_env("SMTP_USE_SSL", False)
        use_tls = _bool_env("SMTP_USE_TLS", not use_ssl)
        return SMTPConfig(
            host=host, port=port, username=username, password=password, use_tls=use_tls, use_ssl=use_ssl
        )

@dataclass
class ReportMailer:
    smtp: SMTPConfig
    from_addr: str
    default_to: List[str] = field(default_factory=list)
    reply_to: Optional[str] = None
    max_retries: int = 3
    backoff_base: float = 1.5

    @staticmethod
    def from_env() -> "ReportMailer":
        smtp = SMTPConfig.from_env()
        from_addr = os.getenv("SMTP_FROM") or (smtp.username or "no-reply@example.com")
        return ReportMailer(smtp=smtp, from_addr=from_addr)

    # ------------------------ Core send ------------------------
    def _connect(self) -> Union[smtplib.SMTP, smtplib.SMTP_SSL]:
        if self.smtp.use_ssl:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(self.smtp.host, self.smtp.port, timeout=self.smtp.timeout, context=context)
        else:
            server = smtplib.SMTP(self.smtp.host, self.smtp.port, timeout=self.smtp.timeout)
        server.ehlo()
        if self.smtp.use_tls and not self.smtp.use_ssl:
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()
        if self.smtp.username and self.smtp.password:
            server.login(self.smtp.username, self.smtp.password)
        return server

    def _attach_files(self, msg: EmailMessage, attachments: Iterable[Union[str, Path]]):
        for path in attachments or []:
            p = Path(path)
            if not p.exists():
                raise FileNotFoundError(f"Attachment not found: {p}")
            ctype, encoding = mimetypes.guess_type(str(p))
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            with p.open("rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=p.name)

    def _embed_images(self, msg: EmailMessage, images: Dict[str, Union[str, Path]]) -> Dict[str, str]:
        """
        images: mapping like {"logo": "path/to/logo.png"}
        Returns: mapping of key -> cid (e.g., {"logo": "cid:..."})
        """
        cid_map: Dict[str, str] = {}
        for key, path in (images or {}).items():
            p = Path(path)
            if not p.exists():
                raise FileNotFoundError(f"Inline image not found: {p}")
            ctype, _ = mimetypes.guess_type(str(p))
            if not ctype or not ctype.startswith("image/"):
                raise ValueError(f"Inline image must be an image type: {p}")
            maintype, subtype = ctype.split("/", 1)
            cid = make_msgid(domain="auto.local")  # e.g., <random@auto.local>
            with p.open("rb") as f:
                msg.get_payload()  # ensure initialized
                msg.add_related(
                    f.read(),
                    maintype=maintype,
                    subtype=subtype,
                    cid=cid.strip("<>"),
                    filename=p.name
                )
            cid_map[key] = f"cid:{cid.strip('<>')}"
        return cid_map

    def _build_message(
        self,
        subject: str,
        to: Optional[Union[AddressLike, Iterable[AddressLike]]] = None,
        html: Optional[str] = None,
        text: Optional[str] = None,
        cc: Optional[Union[AddressLike, Iterable[AddressLike]]] = None,
        bcc: Optional[Union[AddressLike, Iterable[AddressLike]]] = None,
        attachments: Optional[Iterable[Union[str, Path]]] = None,
        inline_images: Optional[Dict[str, Union[str, Path]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[EmailMessage, List[str]]:
        to_list = _coerce_recipients(to) or list(self.default_to)
        cc_list = _coerce_recipients(cc)
        bcc_list = _coerce_recipients(bcc)
        all_rcpts = list(dict.fromkeys(to_list + cc_list + bcc_list))  # dedupe, keep order

        if not all_rcpts:
            raise ValueError("No recipients provided.")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        if self.reply_to:
            msg["Reply-To"] = self.reply_to
        msg["Date"] = formatdate(localtime=True)
        for k, v in (headers or {}).items():
            msg[k] = v

        # multipart/alternative for text + html
        if html and text:
            msg.set_content(text)
            msg.add_alternative(html, subtype="html")
        elif html:
            # Add a plaintext fallback by stripping tags lightly
            import re
            fallback = re.sub("<[^<]+?>", "", html)
            msg.set_content(fallback)
            msg.add_alternative(html, subtype="html")
        elif text:
            msg.set_content(text)
        else:
            msg.set_content("")

        # embed images (as related to the HTML part)
        if inline_images:
            # Ensure we are operating on the HTML part if present
            # EmailMessage with alternatives: payload[-1] is HTML
            part = msg
            if msg.is_multipart():
                # Find the html part
                for p in msg.iter_parts():
                    if p.get_content_type() == "text/html":
                        part = p
                        break
            cid_map = self._embed_images(part, inline_images)
            # Optionally, the caller can format html with these cids beforehand.

        # attachments
        if attachments:
            self._attach_files(msg, attachments)

        return msg, all_rcpts

    def send_report(
        self,
        subject: str,
        to: Optional[Union[AddressLike, Iterable[AddressLike]]] = None,
        html: Optional[str] = None,
        text: Optional[str] = None,
        cc: Optional[Union[AddressLike, Iterable[AddressLike]]] = None,
        bcc: Optional[Union[AddressLike, Iterable[AddressLike]]] = None,
        attachments: Optional[Iterable[Union[str, Path]]] = None,
        inline_images: Optional[Dict[str, Union[str, Path]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Returns the SMTP server response string from sendmail.
        """
        msg, all_rcpts = self._build_message(
            subject=subject, to=to, html=html, text=text, cc=cc, bcc=bcc,
            attachments=attachments, inline_images=inline_images, headers=headers
        )

        attempt = 0
        last_err = None
        while attempt <= self.max_retries:
            try:
                with self._connect() as server:
                    resp = server.sendmail(self.from_addr, all_rcpts, msg.as_string())
                    # sendmail returns a dict of {rcpt: (code, resp)} for failures; empty dict means success
                    if resp:
                        # Some recipients failed
                        failed = ", ".join(f"{k}: {v}" for k, v in resp.items())
                        raise smtplib.SMTPException(f"Some recipients failed: {failed}")
                    return "OK"
            except (smtplib.SMTPException, OSError) as e:
                last_err = e
                if attempt == self.max_retries:
                    raise
                sleep_for = (self.backoff_base ** attempt) + 0.5
                time.sleep(sleep_for)
                attempt += 1
        # Should not reach
        raise RuntimeError(f"Failed to send after retries: {last_err}")

    # --------- Simple template helpers ---------
    def render(self, template: str, **kwargs: Any) -> str:
        """Render using Python str.format(**kwargs)."""
        return template.format(**kwargs)

    def render_template_file(self, path: Union[str, Path], **kwargs: Any) -> str:
        p = Path(path)
        content = p.read_text(encoding="utf-8")
        return self.render(content, **kwargs)

if __name__ == "__main__":
    # Basic smoke test via env-vars (won't actually run in a sandbox without valid SMTP)
    mailer = ReportMailer.from_env()
    print("Mailer ready. From:", mailer.from_addr, "SMTP host:", mailer.smtp.host)
