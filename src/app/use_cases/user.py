import time
import random
from application.ports.users import UserPort
from domain.models.user import UserCreateRequest, User


class UserUseCase:
    def __init__(self, user_repository: UserPort):
        self._user_repository = user_repository

    def _generate_user_id(self) -> str:
        """Generate a unique user ID using timestamp + random."""
        # Get last 5 digits of current timestamp
        timestamp_str = str(int(time.time()))
        last_5_digits = timestamp_str[-5:]
        
        # Generate 4 random digits
        random_4_digits = f"{random.randint(0, 9999):04d}"
        
        return f"u{last_5_digits}{random_4_digits}"

    def create_user(self, user_request: UserCreateRequest) -> User:
        """Create a new user."""
        # Generate user_id if not provided
        if not user_request.user_id:
            user_request.user_id = self._generate_user_id()
        
        return self._user_repository.save(user_request)
