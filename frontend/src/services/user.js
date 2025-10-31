import { API_BASE_URL } from './auth'

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

export async function getCurrentUser() {
  const token = localStorage.getItem('accessToken')

  if (!token) {
    const error = new Error('Usuário não autenticado.')
    error.status = 401
    throw error
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    const detail = await parseError(response)
    const error = new Error(detail)
    error.status = response.status
    throw error
  }

  return response.json()
}

