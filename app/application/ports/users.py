from typing import Protocol
from app.domain.models.user import User


class UserPort(Protocol):

    def get_user_by_id(self, user_id: str) -> User:
        """Get a user by their ID."""

    def save(self, user: User) -> None:
        """Save a user."""
