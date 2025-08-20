from typing import Protocol, Any, Optional


class IdempotencyStore(Protocol):
    def try_start(self, key: str) -> bool:
        """Returns True if this is the first attempt."""
    def complete_success(
            self,
            key: str,
            response: Any) -> None:
        """Mark the operation as successfully completed"""
    def complete_failure(
            self,
            key: str,
            error_code: str,
            message: str) -> None:
        """Mark the operation as failed"""
    def replay(self, key: str) -> Optional[Any]:
        """If the operation was completed successfully,
        return the stored response."""
