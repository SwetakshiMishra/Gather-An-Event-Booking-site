import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()
  if (isLoading) return <main className="page-state shell"><span className="loader" /> Restoring your session...</main>
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" state={{ from: location }} replace />
}

export function AdminRoute() {
  const { isAuthenticated, isLoading, role } = useAuth()
  if (isLoading) return <main className="page-state shell"><span className="loader" /> Restoring your session...</main>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return role === 'admin' ? <Outlet /> : <main className="page-state shell"><h1>Access reserved.</h1><p>You don't have permission to view this area.</p></main>
}