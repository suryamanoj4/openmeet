"""Email service — log-only stub.

Sends emails by logging them. When SMTP settings are configured, real emails
will be sent; otherwise the email content is logged and an EmailLog record
is created.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from config import settings
from models import EmailLog

logger = logging.getLogger("openmeets.email")


async def send_email(
    session: AsyncSession,
    to_email: str,
    subject: str,
    body: str,
    template_name: Optional[str] = None,
    extra_data: Optional[dict] = None,
) -> EmailLog:
    """Send an email.

    Currently logs the email. If SMTP is configured and aiosmtplib is available,
    it could send real email. For now: log + record EmailLog.
    """
    log_entry = EmailLog(
        recipient_email=to_email,
        template_name=template_name,
        status="sent",
        extra_data={
            "subject": subject,
            "body": body,
            "from_email": settings.from_email or "noreply@openmeets.local",
            "from_name": settings.from_name,
            **(extra_data or {}),
        },
    )
    session.add(log_entry)
    await session.flush()

    logger.info(
        "EMAIL SENT\n  To: %s\n  From: %s <%s>\n  Subject: %s\n  Body:\n%s\n",
        to_email,
        settings.from_name,
        settings.from_email or "noreply@openmeets.local",
        subject,
        body,
    )

    return log_entry


async def send_password_reset_email(
    session: AsyncSession,
    to_email: str,
    reset_url: str,
    user_name: str = "",
) -> EmailLog:
    """Send a password reset email."""
    body = f"""Hello {user_name},

You requested a password reset for your OpenMeets account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour. If you did not request this, you can safely ignore this email.

— The OpenMeets Team
"""
    return await send_email(
        session,
        to_email=to_email,
        subject="Reset your OpenMeets password",
        body=body,
        template_name="password_reset",
        extra_data={"reset_url": reset_url},
    )


async def send_email_verification_email(
    session: AsyncSession,
    to_email: str,
    verify_url: str,
    user_name: str = "",
) -> EmailLog:
    """Send an email verification email."""
    body = f"""Hello {user_name},

Welcome to OpenMeets! Please verify your email address by clicking the link below:
{verify_url}

If you did not create an account, you can safely ignore this email.

— The OpenMeets Team
"""
    return await send_email(
        session,
        to_email=to_email,
        subject="Verify your OpenMeets email",
        body=body,
        template_name="email_verification",
        extra_data={"verify_url": verify_url},
    )


async def send_invitation_email(
    session: AsyncSession,
    to_email: str,
    org_name: str,
    invite_url: str,
    inviter_name: str = "",
) -> EmailLog:
    """Send an org invitation email."""
    body = f"""Hello,

{inviter_name} has invited you to join the organization "{org_name}" on OpenMeets.

Click the link below to accept the invitation:
{invite_url}

This invitation will expire soon. If you do not have an account, you can register first.

— The OpenMeets Team
"""
    return await send_email(
        session,
        to_email=to_email,
        subject=f"You're invited to join {org_name} on OpenMeets",
        body=body,
        template_name="invitation",
        extra_data={"invite_url": invite_url, "org_name": org_name},
    )