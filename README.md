# Gather — Event Booking Platform

Gather is a full-stack event booking platform that allows users to discover events, create and manage events, book available seats, and join waitlists when events are full.

The project is built with a **FastAPI backend**, **PostgreSQL database**, and **React + Vite frontend**, with JWT-based authentication, role-based authorization, concurrency-safe booking, and a responsive event-focused interface.

---

## ✨ Features

### 🔐 Authentication & Authorization

* User registration and login
* JWT-based authentication
* Short-lived access tokens
* Long-lived refresh tokens
* Automatic session restoration
* Protected routes
* Role-based authorization
* Admin-only operations
* Password hashing with bcrypt

### 🎫 Event Management

* Create events
* Edit events
* Cancel events
* View event details
* Event categories
* Event locations and venues
* Event capacity management
* Booking opening time
* Automatic event status lifecycle

### 🔎 Event Discovery

* Browse events
* Filter by category
* Filter by location
* Filter by date range
* Pagination
* Sorting
* Upcoming/latest/newest/oldest event ordering
* Responsive event discovery interface

### 🎟️ Booking System

* Book available events
* View personal bookings
* Cancel bookings
* Prevent unauthorized booking cancellation
* Prevent duplicate bookings
* Concurrency-safe seat allocation
* Database-level protection against duplicate bookings

### ⏳ Waitlist System

When an event is full:

* Users can join the waitlist
* Each user receives a waitlist position
* Duplicate waitlist entries are prevented
* Users can leave the waitlist
* Waitlist positions are maintained
* When a booking is cancelled, the first waitlisted user can automatically receive the available seat

### 🕐 Event Lifecycle

Events follow a controlled lifecycle:

```text
UPCOMING
   ↓
ACTIVE
   ↓
CLOSED
```

Events can also be explicitly cancelled:

```text
UPCOMING ─────→ CANCELLED

ACTIVE ───────→ CANCELLED
```

Event status is controlled by the system based on the booking opening time and event date.

Hosts cannot manually change the event status.

---

# 🏗️ Tech Stack

## Backend

* Python
* FastAPI
* SQLModel
* PostgreSQL
* Alembic
* Pydantic
* python-jose
* Passlib
* bcrypt
* psycopg

## Frontend

* React
* Vite
* JavaScript
* Tailwind CSS
* React Router
* ESLint

## Development

* REST API
* JWT Authentication
* OpenAPI / Swagger
* Git & GitHub

---

# 📁 Project Structure

```text
Event-Booking/
│
├── backend/
│   │
│   ├── core/
│   │   └── security.py
│   │
│   ├── Database/
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── booking.py
│   │   └── waitlist.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── booking.py
│   │   └── events.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── booking.py
│   │   └── waitlist.py
│   │
│   ├── services/
│   │
│   ├── main.py
│   └── __init__.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── package-lock.json
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

> The exact frontend structure may evolve as the React application grows.

---

# 🔄 Application Architecture

Gather follows a client-server architecture:

```text
                 ┌──────────────────┐
                 │   React Frontend │
                 │      Gather      │
                 └────────┬─────────┘
                          │
                       REST API
                          │
                          ▼
                 ┌──────────────────┐
                 │  FastAPI Backend │
                 │                  │
                 │ Auth             │
                 │ Events           │
                 │ Bookings         │
                 │ Waitlist         │
                 │ Admin            │
                 └────────┬─────────┘
                          │
                       SQLModel
                          │
                          ▼
                 ┌──────────────────┐
                 │   PostgreSQL     │
                 │     Database     │
                 └──────────────────┘
```

The frontend is responsible for the user interface and client-side state.

The backend remains responsible for:

* Authentication
* Authorization
* Validation
* Business logic
* Seat allocation
* Event lifecycle
* Database operations
* Security

The frontend never acts as a security boundary.

---

# 🔐 Authentication Flow

## Registration

```text
User
 │
 ▼
Registration Form
 │
 ▼
POST /auth/register
 │
 ▼
Password Hashing
 │
 ▼
PostgreSQL
 │
 ▼
User Created
```

Passwords are never stored as plaintext.

---

## Login

```text
User
 │
 ▼
Login Form
 │
 ▼
POST /auth/login
 │
 ▼
Verify Credentials
 │
 ▼
Access Token + Refresh Token
 │
 ▼
React Authentication State
 │
 ▼
Authenticated Application
```

The login endpoint uses OAuth2 password-form authentication.

The frontend therefore sends credentials as form data rather than JSON.

---

## Protected Requests

Authenticated API requests use:

```text
Authorization: Bearer <access_token>
```

The backend extracts the token, verifies its signature and expiration, retrieves the user, and performs authorization checks where required.

---

# 🔄 Access & Refresh Tokens

Gather uses two JWT tokens.

### Access Token

Used for normal authenticated API requests.

It has a short lifetime to reduce the impact of token theft.

### Refresh Token

Used to obtain a new access token when the access token expires.

Conceptually:

```text
Access Token
     │
     │ expires
     ▼
Refresh Token
     │
     ▼
POST /auth/refresh
     │
     ▼
New Access Token
```

The frontend handles session restoration and refreshes authentication when required.

---

# 🎫 Booking Architecture

Booking is designed to remain correct even when multiple users attempt to book the same event at nearly the same time.

The event row is locked during the critical booking operation using PostgreSQL row-level locking.

Conceptually:

```text
Request A ──┐
            │
Request B ──┼──→ Lock Event Row
            │
Request C ──┘
                  │
                  ▼
             Check Capacity
                  │
                  ▼
             Create Booking
                  │
                  ▼
              Commit
```

This ensures that concurrent requests cannot incorrectly allocate the same available seat.

---

# 🛡️ Duplicate Booking Protection

The booking table uses a database-level unique constraint:

```text
(user_id, event_id)
```

This prevents the same user from booking the same event more than once.

The application also checks for existing bookings before creating a new one.

The database constraint provides an additional layer of protection against race conditions.

---

# ⏳ Waitlist Architecture

When an event has no remaining capacity:

```text
User attempts booking
        │
        ▼
Event is full
        │
        ▼
Join Waitlist
        │
        ▼
Position Assigned
```

For example:

```text
User A → Position 1
User B → Position 2
User C → Position 3
```

When a booked seat becomes available:

```text
Booking Cancelled
        │
        ▼
Check Waitlist
        │
   ┌────┴────┐
   │         │
  Yes        No
   │         │
   ▼         ▼
Promote    Increase
first      capacity
waitlisted
user
```

The event row is locked during the cancellation/promotion operation so that seat allocation remains consistent.

---

# 🕐 Event Lifecycle

An event's status is determined by its booking opening time and event date.

### Upcoming

Before booking opens:

```text
now < booking_open_at
```

### Active

Booking is open:

```text
booking_open_at <= now < event_date
```

### Closed

The event date has passed:

```text
now >= event_date
```

### Cancelled

A host explicitly cancels the event.

Cancelled events remain in the database instead of being physically deleted.

---

# 🔎 Event Discovery

The main event discovery endpoint is:

```http
GET /events
```

It supports:

* Category filtering
* Location filtering
* Date range filtering
* Pagination
* Sorting

Available query parameters include:

```text
category
location
start_date
end_date
page
limit
sort
```

Supported sorting options:

```text
upcoming
latest
newest
oldest
```

The API returns pagination metadata including:

* Current page
* Page size
* Total events
* Total pages

---

# 🌐 API Endpoints

## Authentication

| Method | Endpoint         | Description          |
| ------ | ---------------- | -------------------- |
| POST   | `/auth/register` | Register a new user  |
| POST   | `/auth/login`    | Login                |
| POST   | `/auth/refresh`  | Refresh access token |

## Events

| Method | Endpoint             | Description       |
| ------ | -------------------- | ----------------- |
| POST   | `/events`            | Create an event   |
| GET    | `/events`            | Discover events   |
| GET    | `/events/{event_id}` | Get event details |
| PATCH  | `/events/{event_id}` | Edit an event     |
| DELETE | `/events/{event_id}` | Cancel an event   |

## Bookings & Waitlist

| Method | Endpoint                      | Description                 |
| ------ | ----------------------------- | --------------------------- |
| POST   | `/events/{event_id}/book`     | Book event or join waitlist |
| GET    | `/bookings`                   | Get current user's bookings |
| DELETE | `/bookings/{booking_id}`      | Cancel a booking            |
| DELETE | `/events/{event_id}/waitlist` | Leave waitlist              |

## Admin

Administrative operations are available under:

```text
/admin
```

The exact administrative endpoints are documented through the FastAPI OpenAPI documentation.

---

# 🚀 Getting Started

## Prerequisites

Install:

* Python 3.10+
* Node.js
* PostgreSQL
* Git

---

# 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Event-Booking
```

---

# 2. Backend Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 3. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/Event_booking
VITE_API_URL=http://localhost:8000
```

The actual database credentials should never be committed to GitHub.

Use `.env.example` to document the required environment variables without exposing real credentials.

---

# 4. Database Setup

Make sure PostgreSQL is running and the Gather database exists.

Run the Alembic migrations:

```bash
alembic upgrade head
```

This creates and updates the required database tables.

---

# 5. Start the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

---

# 6. Start the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔗 Frontend-Backend Communication

The React frontend communicates with the FastAPI backend using REST API requests.

The frontend API base URL is configured using:

```env
VITE_API_URL=http://localhost:8000
```

Example:

```text
React
 │
 │ POST /auth/login
 ▼
FastAPI
 │
 │ Authenticate
 ▼
PostgreSQL
 │
 ▼
FastAPI
 │
 │ Tokens
 ▼
React
```

---

# 🧪 Testing the Application

A normal user flow:

```text
Register
   ↓
Login
   ↓
Dashboard
   ↓
Explore Events
   ↓
View Event
   ↓
Book Event
   ↓
My Bookings
   ↓
Cancel Booking
```

A waitlist flow:

```text
Create Event
     ↓
Fill Event Capacity
     ↓
Another User Attempts Booking
     ↓
Join Waitlist
     ↓
Existing Booking Cancelled
     ↓
First Waitlisted User Gets Seat
```

---

# 🛡️ Security

Gather currently implements several security measures:

* Password hashing
* JWT authentication
* Access-token expiration
* Refresh tokens
* Protected routes
* Role-based authorization
* Ownership checks
* Database uniqueness constraints
* PostgreSQL row-level locking
* Environment-based configuration
* No backend secrets in the frontend

Frontend authorization checks are used for navigation and UI purposes only.

The backend remains responsible for enforcing permissions.

---

# 🧩 Engineering Highlights

Gather goes beyond a basic CRUD application by addressing several real backend problems.

### Concurrency

Database row locking is used to prevent inconsistent seat allocation when multiple booking requests happen concurrently.

### Data Integrity

Database constraints provide protection against duplicate bookings.

### Authorization

Users can only perform operations they are authorized to perform, while administrative operations are protected separately.

### Event Lifecycle

Event states are derived from booking and event timing instead of allowing arbitrary status manipulation.

### Waitlist Management

Cancelled bookings can automatically promote the first waiting user instead of simply increasing capacity.

### API-Driven Frontend

The React frontend consumes the actual FastAPI API rather than relying on mock or hardcoded event data.

---

# 🚀 Future Roadmap

Gather will gradually evolve toward a more production-oriented architecture.

## 📧 Email Notifications

Add reliable email delivery for:

* Password reset links
* Booking confirmations
* Booking cancellation confirmations
* Waitlist promotion notifications
* Event cancellation notifications
* Event reminders

### Why?

Important event updates should reach users even when they are not actively using Gather.

---

## ⚡ Redis

Introduce Redis for:

* Caching frequently requested event data
* Reducing repeated database queries
* Temporary data
* Rate-limiting support
* Improving API response times

### Why?

Event discovery can generate many repeated requests. Caching frequently accessed information can reduce database load and improve response times.

---

## 🔄 Celery & Background Jobs

Introduce Celery with Redis as a task queue.

Potential background tasks:

* Sending emails
* Sending event reminders
* Automatically updating event statuses
* Cleaning expired reset tokens
* Processing time-consuming operations

### Why?

Slow operations should not block an API request.

For example:

```text
User books event
      │
      ▼
API immediately responds
      │
      ▼
Background worker
      │
      └── Send confirmation email
```

The user does not have to wait for the email operation to finish.

---

## 🔔 WebSockets

Add real-time communication for:

* Live event capacity updates
* Real-time waitlist changes
* Instant booking notifications
* Live seat availability

### Why?

Users should not need to repeatedly refresh an event page to discover that availability has changed.

Future flow:

```text
User A books seat
      │
      ▼
Backend updates database
      │
      ▼
WebSocket event
      │
      ├──────────────→ User B
      │                 "1 seat remaining"
      │
      └──────────────→ User C
                        "Event is now full"
```

---

## 🐳 Docker

Containerize Gather using Docker.

Potential architecture:

```text
                Gather
                  │
        ┌─────────┴─────────┐
        │                   │
    Frontend             Backend
     React                FastAPI
                            │
                    ┌───────┴───────┐
                    │               │
               PostgreSQL         Redis
                                    │
                                  Celery
                                  Worker
```

### Why?

Docker provides a consistent environment for development, testing, and deployment and makes running multiple services easier.

---

## 🧪 Automated Testing

Add automated tests for:

* Authentication
* Event creation
* Event lifecycle
* Booking
* Duplicate booking prevention
* Concurrent booking
* Booking cancellation
* Waitlist promotion
* Authorization
* Admin operations

### Why?

As Gather grows, automated tests will help ensure new features do not break existing functionality.

---

## ☁️ Production Deployment

Deploy Gather to a cloud environment with:

* Production PostgreSQL
* Containerized backend
* Frontend hosting
* Environment-based configuration
* HTTPS
* Production logging
* Monitoring

### Why?

Move Gather from a local development project toward a production-ready application.

---

## 🛡️ Advanced Security

Future security improvements may include:

* Refresh-token rotation
* Refresh-token revocation
* Refresh-token reuse detection
* Rate limiting
* Stronger secret management
* Security headers
* Improved API validation
* Production monitoring

### Why?

As Gather becomes publicly accessible, authentication and API security need additional protection against abuse and token compromise.

---

# 🎯 Project Goal

Gather was built to explore how a real-world event booking platform can handle more than basic CRUD operations.

The project focuses on:

* Authentication
* Authorization
* REST API design
* Database relationships
* Pagination
* Filtering
* Event lifecycle management
* Concurrency
* Seat allocation
* Waitlists
* Frontend-backend integration

A major engineering focus is **maintaining correct seat allocation under concurrent booking requests**.

---

