# Gather — Event Booking Platform

Gather is a full-stack event booking platform where users can discover events, create and manage their own events, book seats, and join a waitlist when an event reaches capacity.

The project was built to go beyond basic CRUD by focusing on authentication, authorization, database integrity, concurrency-safe booking, waitlist management, and event lifecycle handling.

## ✨ Features

### 🔐 Authentication & Authorization

* User registration and login
* JWT-based authentication
* Short-lived access tokens
* Refresh tokens for session restoration
* Protected API routes
* Role-based authorization
* Admin-only operations
* Password hashing with bcrypt

### 🎫 Event Management

* Create events
* Edit and cancel events
* View event details
* Event categories and locations
* Configurable event capacity
* Booking opening time
* Automatic event status management

### 🔎 Event Discovery

Users can browse and discover events using:

* Category filters
* Location filters
* Date-range filters
* Pagination
* Sorting
* Upcoming, latest, newest, and oldest event ordering

### 🎟️ Booking

* Book available events
* View personal bookings
* Cancel bookings
* Prevent duplicate bookings
* Prevent unauthorized cancellation
* Concurrency-safe seat allocation
* Database-level duplicate booking protection

### ⏳ Waitlist

When an event is full, users can join a waitlist.

* Users receive a waitlist position
* Duplicate waitlist entries are prevented
* Users can leave the waitlist
* Cancelled bookings can automatically promote the first waiting user

### 🕐 Event Lifecycle

Events automatically move through their lifecycle based on booking and event times:

```text
UPCOMING
   ↓
ACTIVE
   ↓
CLOSED
```

Events can also be cancelled by their host:

```text
UPCOMING ─────→ CANCELLED

ACTIVE ───────→ CANCELLED
```

Hosts cannot arbitrarily change an event's status. The backend determines the state from the event's timing.

---

# 🏗️ Tech Stack

### Backend

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

### Frontend

* React
* Vite
* JavaScript
* Tailwind CSS
* React Router
* ESLint

### Other

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
│   ├── main.py
│   └── __init__.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── package-lock.json
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🔄 Architecture

Gather uses a client-server architecture.

```text
              ┌─────────────────────┐
              │    React Frontend   │
              │       Gather        │
              └──────────┬──────────┘
                         │
                      REST API
                         │
                         ▼
              ┌─────────────────────┐
              │    FastAPI Backend  │
              │                     │
              │  Authentication     │
              │  Events             │
              │  Bookings           │
              │  Waitlist           │
              │  Admin              │
              └──────────┬──────────┘
                         │
                      SQLModel
                         │
                         ▼
              ┌─────────────────────┐
              │     PostgreSQL      │
              └─────────────────────┘
```

The frontend handles the user interface and client-side state.

The backend is responsible for authentication, authorization, validation, business logic, seat allocation, event lifecycle management, and database operations.

Frontend checks are used for UI and navigation only; **security decisions are enforced by the backend.**

---

# 🔐 Authentication

## Registration

```text
User
 ↓
Registration Form
 ↓
POST /auth/register
 ↓
Password Hashing
 ↓
PostgreSQL
 ↓
User Created
```

Passwords are hashed before being stored and are never stored as plaintext.

## Login

```text
User
 ↓
Login Form
 ↓
POST /auth/login
 ↓
Credential Verification
 ↓
Access Token + Refresh Token
 ↓
Authenticated Application
```

The login endpoint uses OAuth2 password-form authentication, so credentials are submitted as form data.

## Protected Requests

Authenticated requests use:

```text
Authorization: Bearer <access_token>
```

The backend verifies the token, checks its expiration, retrieves the associated user, and performs authorization checks where required.

---

# 🔄 Access & Refresh Tokens

Gather uses two JWT tokens.

### Access Token

Used for normal authenticated API requests and configured with a short lifetime.

### Refresh Token

Used to obtain a new access token after the access token expires.

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

This allows users to remain signed in without requiring them to log in again every time an access token expires.

---

# 🎟️ Booking & Concurrency

One of the main engineering challenges in Gather is preventing **overbooking when multiple users attempt to book the last available seats at the same time.**

A simplified booking flow is:

```text
Booking Request
      ↓
Lock Event Row
      ↓
Check Capacity
      ↓
Create Booking
      ↓
Commit Transaction
```

PostgreSQL row-level locking is used during the critical booking operation.

This prevents concurrent requests from independently seeing the same available capacity and allocating the same seat.

---

# 🛡️ Duplicate Booking Protection

The booking table uses a database-level unique constraint on:

```text
(user_id, event_id)
```

The application also checks for an existing booking before creating one.

The database constraint provides an additional layer of protection against race conditions and duplicate requests.

---

# ⏳ Waitlist

When an event reaches capacity:

```text
User attempts booking
        ↓
Event is full
        ↓
Join Waitlist
        ↓
Waitlist position assigned
```

For example:

```text
User A → Position 1
User B → Position 2
User C → Position 3
```

When an existing booking is cancelled:

```text
Booking Cancelled
       ↓
Check Waitlist
       ↓
First waiting user
       ↓
Seat promoted
```

The cancellation and promotion operation also uses event-level locking to keep seat allocation consistent.

---

# 🕐 Event Lifecycle

An event's status is derived from its booking opening time and event date.

### Upcoming

```text
now < booking_open_at
```

### Active

```text
booking_open_at <= now < event_date
```

### Closed

```text
now >= event_date
```

### Cancelled

A host can cancel an event before or during its lifecycle.

Cancelled events remain in the database rather than being physically deleted.

---

# 🔎 Event Discovery API

The main discovery endpoint is:

```text
GET /events
```

It supports:

* Category filtering
* Location filtering
* Date-range filtering
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

Sorting options include:

```text
upcoming
latest
newest
oldest
```

The API also returns pagination metadata such as:

* Current page
* Page size
* Total events
* Total pages

---

# 🌐 API Endpoints

## Authentication

| Method | Endpoint         | Description          |
| ------ | ---------------- | -------------------- |
| POST   | `/auth/register` | Register a user      |
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

The complete API is available through the automatically generated FastAPI documentation.

---

# 🧪 Example User Flows

### Normal Booking

```text
Register
   ↓
Login
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

### Waitlist

```text
Create Event
      ↓
Event reaches capacity
      ↓
Another user attempts booking
      ↓
Join Waitlist
      ↓
Existing booking is cancelled
      ↓
First waitlisted user is promoted
```

---

# 🛡️ Security & Data Integrity

Gather currently uses:

* Password hashing
* JWT authentication
* Access-token expiration
* Refresh tokens
* Protected API routes
* Role-based authorization
* Ownership checks
* Database uniqueness constraints
* PostgreSQL row-level locking
* Environment-based configuration
* Backend-enforced permissions

The frontend is **not treated as a security boundary**.

Sensitive operations such as authorization, booking validation, and seat allocation are handled by the backend.

---

# 🧩 Engineering Highlights

Gather was designed to address problems that appear in real booking systems rather than stopping at basic CRUD.

### Concurrent Booking

PostgreSQL row-level locking protects seat allocation when multiple requests arrive at the same time.

### Data Integrity

Database constraints prevent duplicate bookings even when application-level checks are bypassed or race with another request.

### Waitlist Promotion

Cancelled bookings can automatically release seats to waiting users instead of simply increasing the event's capacity.

### Event Lifecycle

Event status is derived from time-based rules rather than allowing users to arbitrarily manipulate event states.

### Authorization

Users can only modify resources they are authorized to access, while administrative operations are protected separately.

### API-Driven Frontend

The React application communicates with the actual FastAPI backend through REST APIs rather than relying on hardcoded or mock event data.

---

# 🚀 Roadmap

Gather is currently being developed toward a more production-oriented architecture.

### 📧 Email Notifications

Planned email functionality includes:

* Password reset emails
* Booking confirmations
* Booking cancellation confirmations
* Waitlist promotion notifications
* Event cancellation notifications
* Event reminders

Email functionality is **not currently implemented**.

### ⚡ Redis

Planned uses include:

* Event caching
* Reducing repeated database queries
* Temporary data
* Rate limiting

### 🔄 Background Jobs

Celery with Redis is planned for tasks such as:

* Sending emails
* Event reminders
* Expired-token cleanup
* Other operations that should run outside the request cycle

### 🔔 WebSockets

Planned real-time features include:

* Live seat availability
* Live capacity updates
* Waitlist updates
* Instant booking notifications

### 🐳 Docker

Containerize the application and its supporting services for consistent development and deployment.

Planned architecture:

```text
                Gather
                   │
        ┌──────────┴──────────┐
        │                     │
     React                  FastAPI
     Frontend                Backend
                               │
                    ┌──────────┴──────────┐
                    │                     │
               PostgreSQL              Redis
                                          │
                                       Celery
                                       Worker
```

### 🧪 Automated Testing

Planned test coverage includes:

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

### ☁️ Deployment

Future deployment will include:

* Production PostgreSQL
* Containerized services
* Frontend hosting
* HTTPS
* Production logging
* Monitoring
* Environment-based configuration

### 🛡️ Advanced Security

Planned improvements include:

* Refresh-token rotation
* Refresh-token revocation
* Refresh-token reuse detection
* Rate limiting
* Stronger secret management
* Security headers
* Improved API validation
* Production monitoring

---

# 🎯 Project Goal

Gather was built to explore the engineering challenges behind a real event booking system.

The project focuses on:

* Authentication and authorization
* REST API design
* Database relationships
* Event discovery
* Pagination and filtering
* Event lifecycle management
* Concurrency
* Seat allocation
* Database integrity
* Waitlist management
* React–FastAPI integration

The main engineering challenge is maintaining **correct seat allocation when multiple users attempt to book limited capacity concurrently**.

Rather than treating booking as a simple CRUD operation, Gather uses database-level concurrency control and integrity constraints to keep the system consistent.
