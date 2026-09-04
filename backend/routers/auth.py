from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, select
from backend.core.security import create_access_token, create_refresh_token, decode_access_token, get_current_admin, hash_password,verify_password
from backend.Database.session import get_session
from backend.models.user import User
from backend.schemas.user import User_register, User_login, UserResponse, Token
from backend.core.security import create_reset_token
from backend.models.password_reset import PasswordReset
from backend.schemas.password_reset import ForgotPasswordRequest, ResetPasswordRequest
from backend.services.email_service import send_email
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    if not user:
        return {
            "message": "If an account with this email exists, a password reset link has been sent."
        }

    token = create_reset_token()

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    reset_entry = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )

    session.add(reset_entry)
    session.commit()

    reset_link = f"http://localhost:8000/reset-password?token={token}"

    send_email(
     user.email,
     "Password Reset",
     f"""
    Hello {user.name},

    You requested a password reset.

    Click the link below to reset your password:

    {reset_link}

    This link will expire in 15 minutes.

    If you did not request this, you can ignore this email.
"""
)

    return {
        "message": "If an account with this email exists, a password reset link has been sent."
    }


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    session: Session = Depends(get_session)
):
    reset_entry = session.exec(
        select(PasswordReset).where(
            PasswordReset.token == request.token
        )
    ).first()

    if not reset_entry:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token"
        )

    if reset_entry.used:
        raise HTTPException(
            status_code=400,
            detail="Reset token has already been used"
        )

    if datetime.now(timezone.utc) > reset_entry.expires_at:
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired"
        )

    user = session.get(User, reset_entry.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.password_hash = hash_password(request.new_password)

    reset_entry.used = True

    session.add(user)
    session.add(reset_entry)
    session.commit()

    return {
        "message": "Password reset successfully"
    }


@router.post("/register", response_model=UserResponse)
def register_user(
    user: User_register,
    session: Session = Depends(get_session)
):
    # Check if the user already exists
    statement = select(User).where(User.email == user.email)

    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create a new database User
    new_user = User(
        email=user.email,
        name=user.name,
        age=user.age,
        college=user.college,
        course=user.course,
        graduation_year=user.graduation_year,
        password_hash=hash_password(user.password),
        role="user" ,
    )

    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    except Exception:
        session.rollback()
        raise

    return new_user


@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    statement = select(User).where(
        User.email == form_data.username
    )

    existing_user = session.exec(statement).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {"user_id": existing_user.id},
        expires_delta=timedelta(minutes=15)
    )

    refresh_token = create_refresh_token(
        {"user_id": existing_user.id},
        expires_delta=timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": existing_user.role
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str = Body(..., embed=True),
    session: Session = Depends(get_session)
):
    payload = decode_access_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    access_token = create_access_token(
        {"user_id": user_id},
        expires_delta=timedelta(minutes=15)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": payload.get("role")
    }