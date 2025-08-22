

class UserNotFound(Exception):
    """Raised when a user is not found."""


class FundNotFound(Exception):
    """Raised when a fund is not found."""


class SubscriptionNotFound(Exception):
    """Raised when a subscription is not found."""


class InsufficientBalance(Exception):
    """Raised when a user has insufficient balance for an operation."""


class MinAmountViolation(Exception):
    """Raised when an operation violates the minimum amount requirement."""


class OptimisticLockError(Exception):
    """Raised when an optimistic locking conflict occurs."""


class IdempotencyConflict(Exception):
    """Raised when an idempotent operation conflicts with existing data."""
