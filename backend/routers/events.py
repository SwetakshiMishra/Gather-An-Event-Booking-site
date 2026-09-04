import math

from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.Database.session import get_session
from backend.models import event
from backend.models.event import Event
from backend.models.user import User
from backend.core.security import get_current_user
from backend.schemas.event import EventListResponse, EventUpdate , EventResponse , EventCreate
from datetime import datetime
from sqlmodel import Session, select, func
from typing import Literal

router = APIRouter()

def update_event_status(event: Event):
    now = datetime.utcnow()

    if event.status == "cancelled":
        return

    if now >= event.date:
        event.status = "closed"
    elif now >= event.booking_open_at:
        event.status = "active"



@router.post("/events", response_model=EventResponse)
def create_Event(event:EventCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    new_event = Event(
        name=event.name,
        description=event.description,
        date=event.date,
        booking_open_at=event.booking_open_at,
        location=event.location,
        capacity=event.capacity,
        venue=event.venue,
        category=event.category,
        host_id=current_user.id,
        status="upcoming",  # Set the default status to "upcoming"
    )
    try:
     session.add(new_event)
     session.commit()
     session.refresh(new_event)

    except Exception as e:
     session.rollback()
     print("EVENT CREATION ERROR:", e)

     raise HTTPException(
        status_code=500,
        detail="Error creating event"
    )
    
    return new_event


@router.get("/events", response_model=EventListResponse)
def get_events(
    category: str | None = None,
    location: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort: Literal["upcoming", "latest", "newest", "oldest"] = Query("upcoming"),
    session: Session = Depends(get_session)
):
    statement = select(Event)

    # Apply filters
    if category:
        statement = statement.where(Event.category == category)

    if location:
        statement = statement.where(Event.location == location)

    if start_date:
        statement = statement.where(Event.date >= start_date)

    if end_date:
        statement = statement.where(Event.date <= end_date)


    if sort == "upcoming":
     statement = statement.order_by(Event.date.asc())

    elif sort == "latest":
     statement = statement.order_by(Event.date.desc())

    elif sort == "newest":
     statement = statement.order_by(Event.created_at.desc())

    elif sort == "oldest":
     statement = statement.order_by(Event.created_at.asc())

    

    # Count total matching events
    total = session.exec(
        select(func.count()).select_from(statement.subquery())
    ).one()

    # Apply pagination
    offset = (page - 1) * limit

    statement = statement.offset(offset).limit(limit)

    events = session.exec(statement).all()

    for event in events:
        update_event_status(event)

    session.commit()

    total_pages = math.ceil(total / limit)

    return {
        "events": events,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    session: Session = Depends(get_session)
):
    statement = select(Event).where(Event.id == event_id)
    event = session.exec(statement).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    update_event_status(event)

    session.commit()

    return event

@router.patch("/events/{event_id}", response_model=EventResponse)
def edit_event(
    event_id: int,
    event_data: EventUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(Event).where(
        (Event.id == event_id) &
        (Event.host_id == current_user.id)
    )

    event = session.exec(statement).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )
    update_event_status(event)

    if event.status in ["closed", "cancelled"]:
     raise HTTPException(
        status_code=400,
        detail="This event can no longer be edited"
    )
    update_data = event_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(event, key, value)

    try:
        session.add(event)
        session.commit()
        session.refresh(event)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error updating event"
        )

    return event



@router.delete("/events/{event_id}")
def cancel_event(
    event_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(Event).where(
        (Event.id == event_id) &
        (Event.host_id == current_user.id)
    )

    event = session.exec(statement).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    try:
        event.status = "cancelled"

        session.add(event)
        session.commit()
        session.refresh(event)

    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error cancelling event"
        )

    return {
        "detail": "Event cancelled successfully"
    }