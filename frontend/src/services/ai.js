import { API_BASE_URL } from './auth'

const buildAuthHeaders = () => {
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
    return data?.detail || 'Falha ao se comunicar com a IA.'
  } catch (error) {
    try {
      const text = await response.clone().text()
      return text || 'Falha ao se comunicar com a IA.'
    } catch (innerError) {
      return 'Falha ao se comunicar com a IA.'
    }
  }
}

export async function sendGeminiMessage(message) {
  if (!message?.trim()) {
    throw new Error('Mensagem vazia.')
  }

  const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
    method: 'POST',
    headers: buildAuthHeaders(),
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    const detail = await parseError(response)
    throw new Error(detail)
  }

  return response.json()
}

