import { API_BASE_URL } from './auth'

const authHeaders = () => {
  const token = localStorage.getItem('accessToken')
  if (!token) {
    const error = new Error('Sessão expirada. Faça login novamente.')
    error.status = 401
    throw error
  }

  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

const parseError = async (response) => {
  try {
    const data = await response.clone().json()
    return data?.detail || 'Falha ao carregar dados.'
  } catch (error) {
    try {
      const text = await response.clone().text()
      return text || 'Falha ao carregar dados.'
    } catch (innerError) {
      return 'Falha ao carregar dados.'
    }
  }
}

export async function listRoutes() {
  const response = await fetch(`${API_BASE_URL}/api/routes/`, {
    headers: authHeaders(),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    const error = new Error(detail)
    error.status = response.status
    throw error
  }

  return response.json()
}

export async function getRouteById(routeId) {
  const response = await fetch(`${API_BASE_URL}/api/routes/${routeId}`, {
    headers: authHeaders(),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    const error = new Error(detail)
    error.status = response.status
    throw error
  }

  return response.json()
}

export async function downloadRouteCsv(routeId) {
  const response = await fetch(`${API_BASE_URL}/api/routes/${routeId}/csv`, {
    headers: authHeaders(),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    const error = new Error(detail)
    error.status = response.status
    throw error
  }

  return response.blob()
}

export async function deleteRoutes(routeIds) {
  const response = await fetch(`${API_BASE_URL}/api/routes/`, {
    method: 'DELETE',
    headers: authHeaders(),
    body: JSON.stringify({ route_ids: routeIds }),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    const error = new Error(detail)
    error.status = response.status
    throw error
  }
}

