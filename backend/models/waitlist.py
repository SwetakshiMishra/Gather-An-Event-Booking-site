from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field
if TYPE_CHECKING:
    from backend.models.user import User
    from backend.models.event import Event


class Waitlist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    position: int

    
    user: "User" = Relationship(back_populates="waitlist_entries")
    event: "Event" = Relationship(back_populates="waitlist_entries")