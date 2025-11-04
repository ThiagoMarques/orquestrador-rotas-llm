# Orquestrador Rotas LLM

Aplicação completa para planejamento de rotas turísticas com inteligência artificial. O projeto integra um frontend Vue.js com backend FastAPI, utilizando PostgreSQL como banco de dados e Google Gemini para gerar sugestões inteligentes de rotas baseadas nas cidades cadastradas pelo usuário.

## 🏗️ Arquitetura

- **Frontend**: Vue.js 3 + Vuetify 3
- **Backend**: Python + FastAPI
- **Banco de Dados**: PostgreSQL 16
- **IA**: Google Gemini (via API)
- **Infraestrutura**: Docker Compose (backend, db, pgadmin)


## 🚀 Como executar

### 1. Configurar variáveis de ambiente

Copie o arquivo de exemplo e configure as variáveis:

```bash
cp env.example .env
```

Edite o `.env` e configure principalmente:
- `GEMINI_API_KEY`: sua chave da API do Google Gemini
- `SECRET_KEY`: chave secreta para JWT (use uma string aleatória segura)
- Credenciais do PostgreSQL e pgAdmin

### 2. Subir os serviços

```bash
docker compose up --build
```

Após a inicialização, você terá acesso a:

- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **Documentação Swagger**: `http://localhost:8000/docs`
- **pgAdmin**: `http://localhost:5050`

## 🎯 Funcionalidades

### Autenticação

- Registro de novos usuários
- Login com JWT
- Tokens com expiração configurável
- Proteção de rotas

### Gestão de Cidades

Cadastre cidades com diferentes papéis:
- **Origem**: cidade de partida (uma por usuário)
- **Destino**: cidade de chegada (uma por usuário)
- **Intermediárias**: cidades que podem ser visitadas durante a viagem

Funcionalidades:
- Criar, editar e deletar cidades
- Validação automática de roles (apenas uma origem e uma destino)
- Validação de duplicatas (nome + UF)

### Planejamento de Rotas com IA

O sistema utiliza o Google Gemini para gerar rotas inteligentes baseadas em:
- Cidades cadastradas (origem, destino, intermediárias)
- Histórico de rotas planejadas anteriormente
- Solicitações do usuário em linguagem natural

Cada rota gerada inclui:
- Itinerário completo
- Data prevista de viagem
- Distância e tempo estimado
- Custo estimado
- Tipo de transporte
- Sugestões de hospedagem, alimentação e atividades
- Resumo descritivo

### Interface do Usuário

1. **Card de Cidades**: visualização organizada por tipo (origem, destino, intermediárias)
2. **Card de Rotas Planejadas**: lista todas as rotas geradas com opções de:
   - Ver detalhes completos
   - Baixar CSV individual
   - Seleção múltipla para exclusão
   - Limpar todas as rotas
3. **Card de Sugestões da IA**: destaca a melhor rota recomendada
4. **Chat com IA**: interface de conversa para solicitar novas rotas

## 📡 Endpoints da API

### Autenticação (`/api/auth`)

- `POST /api/auth/register` - Registro de novo usuário
  ```json
  {
    "email": "user@example.com",
    "password": "senha123",
    "full_name": "Nome Completo"
  }
  ```

- `POST /api/auth/login` - Login (form-data)
  - `username`: email do usuário
  - `password`: senha
  - Retorna: `{"access_token": "...", "token_type": "bearer"}`

- `GET /api/auth/me` - Dados do usuário autenticado (requer token)

- `GET /api/health` - Health check da API

### Cidades (`/api/cities`)

Todos os endpoints requerem autenticação.

- `GET /api/cities/` - Lista todas as cidades do usuário
- `POST /api/cities/` - Cria nova cidade
  ```json
  {
    "name": "São Paulo",
    "state": "SP",
    "role": "origin"
  }
  ```
- `PUT /api/cities/{city_id}` - Atualiza cidade existente
- `DELETE /api/cities/{city_id}` - Remove cidade

**Roles válidas**: `origin`, `destination`, `intermediate`

### Rotas (`/api/routes`)

Todos os endpoints requerem autenticação.

- `GET /api/routes/` - Lista todas as rotas do usuário
- `GET /api/routes/{route_id}` - Detalhes completos de uma rota
- `GET /api/routes/{route_id}/csv` - Download da rota em CSV
- `DELETE /api/routes/` - Deleta múltiplas rotas
  ```json
  {
    "route_ids": [1, 2, 3]
  }
  ```

### IA (`/api/ai`)

- `POST /api/ai/chat` - Gera rota com base em mensagem do usuário
  ```json
  {
    "message": "Quero uma rota barata para maio com hospedagem em hotel"
  }
  ```
  Retorna: resposta da IA + lista de rotas criadas

## 🗄️ Acessando o pgAdmin

1. Acesse `http://localhost:5050`
2. Faça login com as credenciais definidas no `.env`:
   - Email: valor de `PGADMIN_DEFAULT_EMAIL`
   - Senha: valor de `PGADMIN_DEFAULT_PASSWORD`
3. Crie um novo servidor:
   - **Name**: `Postgres local` (ou qualquer nome)
   - **Host**: `db`
   - **Port**: `5432`
   - **Username**: valor de `POSTGRES_USER`
   - **Password**: valor de `POSTGRES_PASSWORD`
4. Explore o banco `orquestrador` e suas tabelas:
   - `users`: usuários cadastrados
   - `cities`: cidades cadastradas
   - `route_plans`: rotas planejadas

## 📁 Estrutura do Projeto

```
orquestrador-rotas-llm/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py          # Autenticação
│   │   │   ├── cities.py        # CRUD de cidades
│   │   │   ├── route_plans.py   # Gestão de rotas
│   │   │   └── ai.py            # Integração com Gemini
│   │   ├── services/
│   │   │   └── gemini.py        # Serviço Gemini
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   ├── schemas.py           # Schemas Pydantic
│   │   ├── database.py          # Configuração do banco
│   │   ├── security.py          # JWT e hashing
│   │   ├── config.py            # Configurações
│   │   └── main.py              # App FastAPI
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── HomeView.vue     # Tela principal
│   │   │   ├── LoginView.vue    # Login
│   │   │   └── RegisterView.vue # Registro
│   │   ├── services/
│   │   │   ├── auth.js          # Serviço de autenticação
│   │   │   ├── cities.js        # Serviço de cidades
│   │   │   ├── routes.js        # Serviço de rotas
│   │   │   └── ai.js            # Serviço de IA
│   │   └── ...
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── env.example
└── README.md
```

## 🔧 Tecnologias Utilizadas

### Backend
- FastAPI 
- SQLAlchemy
- PostgreSQL (via psycopg)
- Pydantic
- python-jose (JWT)
- passlib (hashing de senhas)
- google-generativeai

### Frontend
- Vue.js 3
- Vuetify 3
- Vite
- Vue Router

## 🔐 Segurança

- Senhas hasheadas com `pbkdf2_sha256`
- Autenticação via JWT
- Tokens com expiração configurável
- Validação de dados com Pydantic
- Constraints no banco de dados
- CORS configurado
