from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.auth import router as auth_router
from backend.routers.admin import router as admin_router
from backend.routers.booking import router as bookings_router
from backend.routers.events import router as events_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://event-booking-brown.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)

app.include_router(
    bookings_router,
    tags=["Bookings"]
)

app.include_router(
    events_router,
    tags=["Events"]
)