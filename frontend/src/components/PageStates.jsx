export function LoadingState({ label = 'Loading' }) {
  return <div className="page-state"><span className="loader" /> {label}...</div>
}

export function EmptyState({ title, action }) {
  return <div className="empty-state"><span className="empty-mark" aria-hidden="true">+</span><h3>{title}</h3>{action}</div>
}

export function ErrorState({ message, onRetry }) {
  return <div className="error-state"><strong>{message}</strong>{onRetry && <button className="quiet-link button-reset" onClick={onRetry}>Try again</button>}</div>
}