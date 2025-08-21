from typing import Protocol


class Notifier(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> None:
        """Send an email."""
    def send_sms(self, to: str, body: str) -> None:
        """Send an SMS message."""
