from typing import Protocol, Any
from app.domain.models.user import User


class UserPort(Protocol):

    def get_by_id(self, user_id: str) -> User:
        """Get a user by their ID."""

    def update(self, user_id: str, **params: Any) -> User:
        """Update a user."""
