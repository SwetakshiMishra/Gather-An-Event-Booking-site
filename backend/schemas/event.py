from pydantic import BaseModel, Field
from datetime import datetime

class EventCreate(BaseModel):
    name: str
    description: str
    date: datetime
    location: str
    capacity: int = Field(gt=0, description="Capacity must be greater than 0")
    venue: str
    category: str
    booking_open_at: datetime

class EventResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    date: datetime
    booking_open_at: datetime
    venue: str
    capacity: int
    host_id: int
    status: str

class EventUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    date: datetime | None = None
    location: str | None = None
    capacity: int | None = Field(default=None, gt=0, description="Capacity must be greater than 0")
    venue: str | None = None
    category: str | None = None


#for pagination

class EventListResponse(BaseModel):
    events: list[EventResponse]
    page: int
    limit: int
    total: int
    total_pages: int