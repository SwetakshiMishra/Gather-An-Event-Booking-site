from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.models.waitlist import Waitlist
from backend.Database.session import get_session
from backend.models.booking import Booking
from backend.models.event import Event
from backend.models.user import User
from backend.core.security import get_current_user
from backend.schemas.waitlist import WaitlistResponse
from backend.schemas.booking import BookingEvent
from backend.routers.events import update_event_status

router = APIRouter()


# Get all bookings of the current user
@router.get("/bookings")
def get_bookings(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Booking).where(
        Booking.user_id == current_user.id
    )

    bookings = session.exec(statement).all()

    return bookings


# Book an event
@router.post( 
    "/events/{event_id}/book", 
    response_model=BookingEvent | WaitlistResponse 
) 
def book_event( 
    event_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session) 
): 
    
    # Lock event row 
    statement = ( 
        select(Event) 
        .where(Event.id == event_id) 
        .with_for_update() 
    ) 
    event = session.exec(statement).first() 
 
    if not event: 
        raise HTTPException( 
            status_code=404, 
            detail="Event not found" 
        ) 
    update_event_status(event)

    if event.status != "active":
     raise HTTPException(
        status_code=400,
        detail="Booking is not currently open"
    )
    
    # Already booked? 
    statement = select(Booking).where( 
        Booking.user_id == current_user.id, 
        Booking.event_id == event_id 
    ) 
    existing_booking = session.exec(statement).first() 
 
    if existing_booking: 
        raise HTTPException( 
            status_code=400, 
            detail="You have already booked this event" 
        ) 
 
    # Event full → waitlist 
    if event.capacity <= 0: 
 
        existing = session.exec( 
            select(Waitlist).where( 
                Waitlist.user_id == current_user.id, 
                Waitlist.event_id == event_id 
            ) 
        ).first() 
 
        if existing: 
            raise HTTPException( 
                status_code=400, 
                detail="You are already on the waitlist" 
            ) 
 
        waitlist_entries = session.exec( 
            select(Waitlist).where( 
                Waitlist.event_id == event_id 
            ) 
        ).all() 
 
        position = len(waitlist_entries) + 1 
 
        new_entry = Waitlist( 
            user_id=current_user.id, 
            event_id=event_id, 
            position=position 
        ) 
 
        session.add(new_entry) 
        session.commit() 
        session.refresh(new_entry) 
 
        return new_entry 
 
    # Create booking 
    new_booking = Booking( 
        user_id=current_user.id, 
        event_id=event_id 
    ) 
 
    event.capacity -= 1 
 
    try: 
        session.add(new_booking) 
        session.commit() 
        session.refresh(new_booking) 
 
    except Exception: 
        session.rollback() 
        raise HTTPException( 
            status_code=500, 
            detail="Error booking event" 
        ) 
 
    return new_booking


@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    booking = session.get(Booking, booking_id)

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to cancel this booking"
        )

    # Lock the event
    statement = (
        select(Event)
        .where(Event.id == booking.event_id)
        .with_for_update()
    )
    event = session.exec(statement).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    try:
        # Find first person on waitlist
        statement = (
            select(Waitlist)
            .where(Waitlist.event_id == event.id)
            .order_by(Waitlist.position)
        )
        waitlist_entry = session.exec(statement).first()

        # Remove cancelled booking
        session.delete(booking)

        if waitlist_entry:
            # Give the seat directly to waitlisted user
            new_booking = Booking(
                user_id=waitlist_entry.user_id,
                event_id=event.id
            )

            session.add(new_booking)
            session.delete(waitlist_entry)

            message = "Booking cancelled. Waitlisted user got the seat."

        else:
            # Nobody waiting → return seat to event
            event.capacity += 1
            message = "Booking cancelled successfully."

        session.commit()

    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error cancelling booking"
        )

    return {
        "message": message
    }


# View one specific booking
@router.get("/bookings/{booking_id}")
def view_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Booking).where(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    )

    booking = session.exec(statement).first()

    

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking

#check all bookings of your event

@router.get("/events/{event_id}/bookings")
def get_event_bookings(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Check if the event exists and belongs to the current user
    event = session.get(Event, event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    if event.host_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view bookings for this event"
        )

    # Get all bookings for the event
    statement = select(Booking).where(Booking.event_id == event_id)
    bookings = session.exec(statement).all()

    return bookings


#remove yourself from waitlist
@router.delete("/events/{event_id}/waitlist")
def leave_waitlist(
    event_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Lock the event row
    statement = (
        select(Event)
        .where(Event.id == event_id)
        .with_for_update()
    )

    event = session.exec(statement).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    # Find user's waitlist entry
    statement = select(Waitlist).where(
        (Waitlist.event_id == event_id) &
        (Waitlist.user_id == current_user.id)
    )

    entry = session.exec(statement).first()

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="You are not on the waitlist"
        )

    removed_position = entry.position

    try:
        session.delete(entry)

        # Move everyone behind them one position forward
        remaining = session.exec(
            select(Waitlist)
            .where(
                (Waitlist.event_id == event_id) &
                (Waitlist.position > removed_position)
            )
            .order_by(Waitlist.position)
        ).all()

        for item in remaining:
            item.position -= 1

        session.commit()

    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error leaving waitlist"
        )

    return {
        "message": "You have been removed from the waitlist"
    }