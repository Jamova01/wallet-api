from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
import uuid
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from app.models import User


class Account(SQLModel, table=True):
    """
    Represents a financial account within the digital wallet system.

    This model stores the core state of a user's account, including balances,
    account type, currency, and lifecycle status. It is designed following
    standard fintech patterns used by modern neobanks.

    Attributes:
        id (uuid.UUID):
            Unique identifier for the account.
        user_id (uuid.UUID):
            Identifier of the user who owns the account.
        type (str):
            The type of account (e.g., "checking", "savings", "main", "pocket").
        currency (str):
            ISO currency code associated with the account (e.g., "COP", "USD").
        status (str):
            Lifecycle state of the account. Common values include:
            - "active": account fully operational
            - "frozen": temporarily restricted
            - "closed": permanently deactivated
        balance (Decimal):
            The accounting balance. Represents the sum derived from the
            double-entry ledger. Stored for optimization but logically derived.
        available_balance (Decimal):
            Funds the user can actually spend. Generally equals:
            `balance - holds - pending_transactions`.
        created_at (datetime):
            Timestamp when the account record was created (UTC).
        updated_at (datetime):
            Timestamp when the account record was last updated (UTC).
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    user: Optional["User"] = Relationship(back_populates="accounts")

    type: str = Field(default="main")

    currency: str = Field(default="COP", max_length=3)

    status: str = Field(default="active")

    balance: Decimal = Field(default=0)

    available_balance: Decimal = Field(default=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
