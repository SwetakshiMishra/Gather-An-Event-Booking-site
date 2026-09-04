from datetime import datetime
from pydantic import BaseModel


class WaitlistResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    position: int
    created_at: datetime