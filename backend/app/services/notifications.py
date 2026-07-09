"""Notification stub.

A real deployment would send email/SMS/push via a provider (SES, Twilio,
etc.). For this project the "send" is mocked as a log line — wiring in a
real provider is a config/credentials change, not an architecture change,
since callers only depend on `notify_irrigate_soon`.
"""

import logging

logger = logging.getLogger("aquasense.notifications")


def notify_irrigate_soon(user_email: str, field_name: str, irrigation_date: str) -> None:
    logger.info(
        "[MOCK NOTIFICATION] To: %s | Subject: Irrigate '%s' soon | "
        "Body: Our forecast projects '%s' will need irrigation on %s.",
        user_email,
        field_name,
        field_name,
        irrigation_date,
    )
