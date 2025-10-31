import { API_BASE_URL } from './auth'

const buildAuthHeaders = () => {
  const token = localStorage.getItem('accessToken')
  if (!token) {
    throw new Error('Autenticação expirada. Faça login novamente.')
  }

  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

const parseError = async (response) => {
  try {
    const data = await response.clone().json()
    return data?.detail || 'Falha ao processar sua solicitação.'
  } catch (error) {
    try {
      const text = await response.clone().text()
      return text || 'Falha ao processar sua solicitação.'
    } catch (innerError) {
      return 'Falha ao processar sua solicitação.'
    }
  }
}

export async function listCities() {
  const response = await fetch(`${API_BASE_URL}/api/cities/`, {
    headers: buildAuthHeaders(),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    const error = new Error(detail)
    error.status = response.status
    throw error
  }

  return response.json()
}

export async function createCity(payload) {
  const response = await fetch(`${API_BASE_URL}/api/cities/`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    throw new Error(detail)
  }

  return response.json()
}

export async function updateCity(cityId, payload) {
  const response = await fetch(`${API_BASE_URL}/api/cities/${cityId}`, {
    method: 'PUT',
    headers: buildAuthHeaders(),
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    throw new Error(detail)
  }

  return response.json()
}

export async function deleteCity(cityId) {
  const response = await fetch(`${API_BASE_URL}/api/cities/${cityId}`, {
    method: 'DELETE',
    headers: buildAuthHeaders(),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    throw new Error(detail)
  }
}

