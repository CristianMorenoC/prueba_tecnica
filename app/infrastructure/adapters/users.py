from app.infraestructure.adapters.users import UserPort, PublicUser
from app.domain.models.user import User
from typing import Dict


class UserAdapter(UserPort):
    def __init__(self):
        self.users: Dict[str, User] = {}

    def get_user_by_id(self, user_id: str) -> User:
        """Get a user by their ID."""
        user_data = self.user_repository.find_by_id(user_id)
        user_data = {
            "user_id": "USER123",
            "name": "John Doe",
            "email": "jhon@email.com",
            "phone": "1234567890",
            "balance": 100.0,
            "notify_channel": "email"
        }
        if not user_data:
            raise ValueError("User not found")
        return User(**user_data)

    def save(self, user: User) -> PublicUser:
        """Save a user."""
        self.user_repository.save(user.to_dict())
        return {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "balance": user.balance,
            "notify_channel": user.notify_channel.value
        }
