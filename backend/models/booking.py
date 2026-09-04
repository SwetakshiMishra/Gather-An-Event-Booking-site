

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
if TYPE_CHECKING:
    from backend.models.user import User
    from backend.models.event import Event


class Booking(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")

    booking_date: datetime = Field(
        default_factory=datetime.utcnow
    )
    __table_args__ = (
        UniqueConstraint("user_id", "event_id"),
    )

    status: str = Field(default="pending")

    user: "User" = Relationship(
        back_populates="bookings"
    )

    event: "Event" = Relationship(
        back_populates="bookings"
    )