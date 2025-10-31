# Orquestrador Rotas LLM

Projeto base para um orquestrador de rotas com frontend em Vue.js, backend em Python (FastAPI) e banco de dados PostgreSQL.

## Pré-requisitos

- Docker e Docker Compose instalados.
- Arquivo de variáveis de ambiente (copie `env.example` para `.env`).

```bash
cp env.example .env
```

## Executando a stack

```bash
docker compose up --build
```

- API disponível em `http://localhost:8000`
- Documentação automática (Swagger) em `http://localhost:8000/docs`

## Endpoints iniciais

- `POST /api/auth/register`: cria um novo usuário (campos: `email`, `password`, `full_name`).
- `POST /api/auth/login`: autenticação via OAuth2 (enviar `username` e `password` como `form-data`). Retorna token JWT.
- `GET /api/auth/me`: retorna dados do usuário autenticado (enviar header `Authorization: Bearer <token>`).
- `GET /api/health`: verificação simples da API.


