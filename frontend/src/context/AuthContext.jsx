import { useEffect, useMemo, useState } from 'react'
import { loginRequest, refreshRequest } from '../api/client'
import { AuthContext } from './auth-context'

const STORAGE_KEY = 'gather-auth'

function getUserId(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return payload.user_id
  } catch {
    return null
  }
}

  function isAccessTokenUsable(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
      return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now()
    } catch {
      return false
    }
  }

function readStoredAuth() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || null } catch { return null }
}

export function AuthProvider({ children }) {
  const initialAuth = useMemo(() => readStoredAuth(), [])
  const [auth, setAuth] = useState(() => initialAuth)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function restore() {
      try {
          if (initialAuth?.accessToken && isAccessTokenUsable(initialAuth.accessToken)) {
            if (!cancelled) setAuth(initialAuth)
          } else if (initialAuth?.refreshToken) {
          const token = await refreshRequest(initialAuth.refreshToken)
          if (!cancelled) setAuth((current) => ({ ...current, accessToken: token.access_token, role: token.role || current.role }))
          } else {
          if (!cancelled) setAuth(null)
        }
      } catch {
        if (!cancelled) setAuth(null)
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }
    restore()
    return () => { cancelled = true }
  }, [initialAuth])

  useEffect(() => {
    if (auth) localStorage.setItem(STORAGE_KEY, JSON.stringify(auth))
    else localStorage.removeItem(STORAGE_KEY)
  }, [auth])

  const value = useMemo(() => ({
    auth,
    isLoading,
    isAuthenticated: Boolean(auth?.accessToken),
    role: auth?.role || null,
    async login(email, password) {
      const result = await loginRequest(email, password)
      setAuth({ accessToken: result.access_token, refreshToken: result.refresh_token, role: result.role, userId: getUserId(result.access_token) })
      return result
    },
    async refresh() {
      if (!auth?.refreshToken) return null
      try {
        const result = await refreshRequest(auth.refreshToken)
        setAuth((current) => current ? { ...current, accessToken: result.access_token, role: result.role || current.role } : current)
        return result.access_token
      } catch {
        setAuth(null)
        return null
      }
    },
    logout() { setAuth(null) },
  }), [auth, isLoading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}