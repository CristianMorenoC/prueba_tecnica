from typing import Protocol, Any
from domain.models.user import User, UserCreateRequest


class UserPort(Protocol):

    def get_by_id(self, user_id: str) -> User:
        """Get a user by their ID."""

    def update(self, user_id: str, **params: Any) -> User:
        """Update a user."""

    def save(self, user: UserCreateRequest) -> User:
        """Save a user."""
