from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.Database.session import get_session
from backend.models.booking import Booking
from backend.models.user import User
from backend.core.security import get_current_admin


router = APIRouter()

@router.get("/bookings/{booking_id}")
def get_booking(
    booking_id:int,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
    ):
    statement = select(Booking).where(
        Booking.id == booking_id
    )
    booking = session.exec(statement).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )
    return booking

@router.patch("/role/{user_id}")
def update_user_role(
    user_id: int,
    new_role: str,
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    statement= select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if new_role not in ["user", "admin"]:
     raise HTTPException(
        status_code=400,
        detail="Invalid role"
    )

    if user.id == admin.id and new_role != "admin":
     raise HTTPException(
        status_code=400,
        detail="You cannot remove your own admin role"
    )
    user.role = new_role
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


