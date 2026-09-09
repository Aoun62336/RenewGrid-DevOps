"""
services/email_service.py — Transactional email delivery via SMTP.

Configuration is read from environment variables (see .env):
  SMTP_HOST   — SMTP server hostname      (default: smtp.gmail.com)
  SMTP_PORT   — SMTP server port          (default: 587, STARTTLS)
  SMTP_USER   — Sender address / login    (required)
  SMTP_PASS   — SMTP password / app-pwd   (required)
  FRONTEND_URL — Base URL for reset links (default: http://localhost:5173)

Gmail quick-start:
  1. Enable 2-Step Verification on your Google account.
  2. Go to Google Account → Security → App Passwords.
  3. Generate an app password for "Mail" + your device.
  4. Set SMTP_USER=your@gmail.com and SMTP_PASS=<app-password> in .env.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── HTML email template ───────────────────────────────────────────────────────
_RESET_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Reset Your RenewGrid Password</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 0;">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;
                      box-shadow:0 2px 8px rgba(0,0,0,.08);overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="background:#16a34a;padding:32px 40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:24px;letter-spacing:-0.5px;">
                ♻️ RenewGrid
              </h1>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 24px;">
              <h2 style="margin:0 0 16px;color:#111827;font-size:20px;">
                Password Reset Request
              </h2>
              <p style="margin:0 0 24px;color:#4b5563;line-height:1.6;">
                We received a request to reset the password for your RenewGrid
                account. Click the button below to choose a new password. This
                link expires in <strong>30 minutes</strong>.
              </p>
              <div style="text-align:center;margin-bottom:32px;">
                <a href="{reset_url}"
                   style="display:inline-block;padding:14px 32px;
                          background:#16a34a;color:#ffffff;
                          text-decoration:none;border-radius:6px;
                          font-size:16px;font-weight:bold;">
                  Reset My Password
                </a>
              </div>
              <p style="margin:0 0 8px;color:#6b7280;font-size:13px;">
                Or copy and paste this URL into your browser:
              </p>
              <p style="margin:0;word-break:break-all;color:#16a34a;font-size:13px;">
                {reset_url}
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px 40px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;line-height:1.6;">
                If you did not request a password reset, you can safely ignore
                this email — your password will not be changed.<br/><br/>
                © 2025 RenewGrid. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

_RESET_PLAIN = (
    "RenewGrid — Password Reset\n\n"
    "We received a request to reset your password.\n\n"
    "Click the link below (valid for 30 minutes):\n"
    "{reset_url}\n\n"
    "If you did not request this, you can ignore this email.\n\n"
    "— The RenewGrid Team"
)


def send_reset_email(to_email: str, reset_token: str) -> None:
    """
    Send a password-reset email to *to_email*.

    Constructs the reset URL from settings.FRONTEND_URL and the supplied token,
    then dispatches via SMTP with STARTTLS. Designed to run as a BackgroundTask.
    """
    try:
        if not settings.SMTP_USER or not settings.SMTP_PASS:
            logger.error("SMTP credentials are not configured. Cannot send email to %s", to_email)
            return

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        # ── Build message ─────────────────────────────────────────────────────────
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset Your RenewGrid Password"
        msg["From"]    = f"RenewGrid <{settings.SMTP_USER}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(_RESET_PLAIN.format(reset_url=reset_url), "plain"))
        msg.attach(MIMEText(_RESET_HTML.format(reset_url=reset_url),  "html"))

        # ── Send ──────────────────────────────────────────────────────────────────
        logger.info("Sending password-reset email to %s via %s:%d",
                    to_email, settings.SMTP_HOST, settings.SMTP_PORT)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

        logger.info("Password-reset email sent successfully to %s.", to_email)
    except Exception:
        logger.exception("Failed to send password-reset email to %s.", to_email)
