
from pydantic import BaseModel, Field
from datetime import datetime

class BookingEvent(BaseModel):
    id: int
    user_id: int
    event_id: int
    booking_date: datetime
    status: str
    