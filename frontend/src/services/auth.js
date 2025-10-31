const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '')

const buildLoginBody = ({ email, password }) => {
  const params = new URLSearchParams()
  params.set('username', email)
  params.set('password', password)
  params.set('scope', '')
  params.set('grant_type', '')
  params.set('client_id', '')
  params.set('client_secret', '')
  return params
}

const parseError = async (response) => {
  try {
    const data = await response.clone().json()
    return data?.detail || 'Falha na autenticação.'
  } catch (error) {
    try {
      const text = await response.clone().text()
      return text || 'Falha na autenticação.'
    } catch (innerError) {
      return 'Falha na autenticação.'
    }
  }
}

export async function login({ email, password }) {
  if (!email || !password) {
    throw new Error('Informe e-mail e senha para continuar.')
  }

  let response

  try {
    response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: buildLoginBody({ email, password }),
    })
  } catch (error) {
    throw new Error('Não foi possível conectar ao servidor. Verifique sua rede.')
  }

  if (!response.ok) {
    const detail = await parseError(response)
    throw new Error(detail)
  }

  const data = await response.json()

  if (!data?.access_token) {
    throw new Error('Resposta inválida do servidor.')
  }

  return data.access_token
}

