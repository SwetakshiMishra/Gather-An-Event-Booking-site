export default function Modal({ title, children, confirmLabel = 'Confirm', onConfirm, onClose, busy = false }) {
  return <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" onMouseDown={(event) => event.stopPropagation()}>
      <button className="modal-close" onClick={onClose} aria-label="Close">×</button>
      <h2 id="modal-title">{title}</h2>
      <div className="modal-copy">{children}</div>
      <div className="modal-actions"><button className="button button-muted" onClick={onClose}>Cancel</button><button className="button" onClick={onConfirm} disabled={busy}>{busy ? 'Working...' : confirmLabel}</button></div>
    </div>
  </div>
}