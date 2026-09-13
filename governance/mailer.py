"""Outbound email.

This module is deliberately NOT a Strands tool, and nothing here is decorated
with @tool. It lives in governance/ beside the approve/reject functions for the
same reason those aren't tools either: the Donor Steward must have no reachable
path to sending. The web layer calls this, and only after a human has approved.

If sending fails, approval still stands. A human decision is not rolled back
because an email provider had a bad minute — the failure is recorded instead.
"""
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API = "https://api.resend.com/emails"


def send_donor_message(to: str, subject: str, body: str) -> tuple[bool, str]:
    """Send an approved donor message. Returns (sent, detail).

    Never raises — the caller is a human clicking a button, and a provider
    outage should not look like a failed approval.
    """
    key = os.getenv("RESEND_API_KEY")
    if not key:
        return False, "no RESEND_API_KEY configured"

    sender = os.getenv("FOYER_FROM_EMAIL", "onboarding@resend.dev")

    try:
        r = httpx.post(
            API,
            headers={"Authorization": f"Bearer {key}"},
            json={"from": sender, "to": [to], "subject": subject, "text": body},
            timeout=15,
        )
        if r.status_code >= 400:
            return False, f"provider returned {r.status_code}: {r.text[:160]}"
        return True, f"delivered to {to}"
    except Exception as exc:
        return False, f"send failed: {type(exc).__name__}"
