from typing import Protocol, Optional
from app.domain.models.auth import Credentials


class AuthRepo(Protocol):
    def get_by_username(self, username: str) -> Optional[Credentials]:
        """Get credentials by username."""
    def create_credentials(self, creds: Credentials) -> None:
        """Create new credentials."""
    def username_exists(self, username: str) -> bool:
        """Check if a username already exists."""


class PasswordHasher(Protocol):
    def hash(self, raw_password: str) -> str:
        """Hash a raw password."""
    def verify(self, raw_password: str, hashed: str) -> bool:
        """Verify a raw password against a hashed password."""
