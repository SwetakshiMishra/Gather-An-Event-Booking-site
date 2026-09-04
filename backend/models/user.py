
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from backend.models.waitlist import Waitlist

if TYPE_CHECKING:
    from backend.models.booking import Booking
    from backend.models.event import Event


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(unique=True, index=True)
    name: str
    age: int | None = None
    college: str
    course: str
    graduation_year: int
    password_hash: str
    role: str = Field(default="user")

    bookings: list["Booking"] = Relationship(
        back_populates="user"
    )
    waitlist_entries: list["Waitlist"] = Relationship(
    back_populates="user"
)
    hosted_events: list["Event"] = Relationship(
        back_populates="host"
    )