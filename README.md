# Orquestrador Rotas LLM

Projeto base para um orquestrador de rotas com frontend em Vue.js, backend em Python (FastAPI) e banco de dados PostgreSQL.

## Pré-requisitos

- Docker e Docker Compose instalados.
- Durante o build da imagem do backend é necessário instalar dependências nativas para o `psycopg[binary]`. Caso personalize o Dockerfile, inclua o comando:
  ```Dockerfile
  RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
   && rm -rf /var/lib/apt/lists/*
  ```
- Arquivo de variáveis de ambiente (copie `env.example` para `.env`).

```bash
cp env.example .env
```

## Variáveis de ambiente

- Copie `env.example` para `.env` na raiz do projeto para configurar backend, banco de dados e pgAdmin.
- No frontend, utilize o arquivo `frontend/.env.example` como base e ajuste a variável `VITE_API_BASE_URL` caso necessário (há um arquivo `frontend/.env.development` pré-configurado para uso local).

```bash
cp env.example .env
cp frontend/.env.example frontend/.env.local # opcional, para sobrescrever valores locais
```

## Executando a stack

```bash
docker compose up --build
```

- Frontend disponível em `http://localhost:5173`
- API disponível em `http://localhost:8000`
- Documentação automática (Swagger) em `http://localhost:8000/docs`
- pgAdmin disponível em `http://localhost:5050` (use `PGADMIN_DEFAULT_EMAIL` e `PGADMIN_DEFAULT_PASSWORD` definidos no `.env`).

## Primeira tela de login

O frontend inicia com uma tela de login que consome o endpoint `POST /api/auth/login`. Informe e-mail e senha de um usuário previamente cadastrado (via endpoint `POST /api/auth/register`). Em caso de sucesso, o token JWT é armazenado em `localStorage` para uso futuro.

## Endpoints iniciais

- `POST /api/auth/register`: cria um novo usuário (campos: `email`, `password`, `full_name`).
- `POST /api/auth/login`: autenticação via OAuth2 (enviar `username` e `password` como `form-data`). Retorna token JWT.
- `GET /api/auth/me`: retorna dados do usuário autenticado (enviar header `Authorization: Bearer <token>`).
- `GET /api/health`: verificação simples da API.

## Acessando o pgAdmin

1. Abra `http://localhost:5050` e faça login com as credenciais definidas nas variáveis `PGADMIN_DEFAULT_EMAIL` e `PGADMIN_DEFAULT_PASSWORD` do `.env`.
2. Crie um novo servidor e configure:
   - **Name**: qualquer identificação (ex.: `Postgres local`).
   - **Host**: `db` (nome do serviço Docker).
   - **Port**: `5432`.
   - **Username**: valor de `POSTGRES_USER`.
   - **Password**: valor de `POSTGRES_PASSWORD`.
3. Após salvar, você poderá explorar o banco `orquestrador`, consultar tabelas e executar queries diretamente pelo navegador.


