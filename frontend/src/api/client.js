const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function getFriendlyMessage(status, detail) {
  if (status === 400) return detail || 'Please check the information and try again.'
  if (status === 401 && detail === 'Invalid email or password') return 'Incorrect email or password.'
  if (status === 401) return 'Your session has expired. Please log in again.'
  if (status === 403) return "You don't have permission to perform this action."
  if (status === 404) return "We couldn't find what you were looking for."
  if (status === 422) return 'Some information needs attention before continuing.'
  if (status >= 500) return 'Something went wrong. Please try again.'
  return detail || 'Something went wrong. Please try again.'
}

async function readResponse(response) {
  const contentType = response.headers.get('content-type') || ''
  const body = contentType.includes('application/json') ? await response.json() : await response.text()
  if (!response.ok) {
    const detail = typeof body === 'object' && body?.detail
      ? Array.isArray(body.detail) ? body.detail.map((item) => item.msg).join(', ') : body.detail
      : undefined
    throw new ApiError(response.status, getFriendlyMessage(response.status, detail))
  }
  return body
}

export async function request(path, options = {}, auth = {}, retry = true) {
  const headers = new Headers(options.headers || {})
  const isForm = options.body instanceof URLSearchParams
  if (!isForm && options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  if (auth.accessToken) headers.set('Authorization', `Bearer ${auth.accessToken}`)

  let response
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10000)
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers, signal: options.signal || controller.signal })
  } catch (error) {
    if (error.name === 'AbortError') throw new ApiError(0, "The Gather API took too long to respond. Make sure the backend is running on port 8000.")
    throw new ApiError(0, "Can't connect to the Gather API. Make sure the backend is running on port 8000 and that CORS allows http://localhost:5173.")
  } finally {
    clearTimeout(timeoutId)
  }

  if (response.status === 401 && retry && auth.refreshToken && auth.onRefresh && path !== '/auth/refresh') {
    const refreshed = await auth.onRefresh()
    if (refreshed) return request(path, options, { ...auth, accessToken: refreshed }, false)
  }
  return readResponse(response)
}

export function apiGet(path, auth) {
  return request(path, { method: 'GET' }, auth)
}

export function apiPost(path, body, auth) {
  return request(path, { method: 'POST', body: JSON.stringify(body) }, auth)
}

export function apiPatch(path, body, auth) {
  return request(path, { method: 'PATCH', body: JSON.stringify(body) }, auth)
}

export function apiDelete(path, auth) {
  return request(path, { method: 'DELETE' }, auth)
}

export async function loginRequest(email, password) {
  const body = new URLSearchParams({ username: email, password })
  return request('/auth/login', { method: 'POST', body })
}

export function refreshRequest(refreshToken) {
  return apiPost('/auth/refresh', { refresh_token: refreshToken })
}

export { API_URL }