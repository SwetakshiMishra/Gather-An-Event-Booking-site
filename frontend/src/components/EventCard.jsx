import { Link } from 'react-router-dom'

function formatDate(value) {
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value))
}

export default function EventCard({ event }) {
  return (
    <Link className="event-card" to={`/events/${event.id}`}>
      <div className="event-card-art" aria-hidden="true"><span>{event.category?.slice(0, 1).toUpperCase()}</span></div>
      <div className="event-card-body">
        <div className="card-meta"><span className="tag">{event.category}</span><span>{formatDate(event.date)}</span></div>
        <h3>{event.name}</h3>
        <p>{event.description}</p>
        <div className="card-footer"><span>{event.venue}</span><span className={`status status-${event.status}`}>{event.status}</span></div>
      </div>
    </Link>
  )
}