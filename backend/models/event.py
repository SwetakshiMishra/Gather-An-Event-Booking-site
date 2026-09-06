

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from backend.models.waitlist import Waitlist

if TYPE_CHECKING:
    from backend.models.user import User
    from backend.models.booking import Booking


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str
    description: str
    date: datetime
    location: str
    capacity: int
    venue: str
    category: str
    status: str
    booking_open_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    host_id: int = Field(foreign_key="user.id")

    host: "User" = Relationship(
        back_populates="hosted_events"
    )

    waitlist_entries: list["Waitlist"] = Relationship(
        back_populates="event"
    )

    bookings: list["Booking"] = Relationship(
        back_populates="event"
    )