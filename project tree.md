# AI School Recommendation System

An intelligent school recommendation system powered by Agentic RAG, helping students find the best-fit universities based on their academic profile, preferences, and priorities.

## Features

- **Intelligent Matching**: Two-phase recommendation system combining structured filtering and semantic similarity
- **User Profile Collection**: Multi-step form to collect comprehensive user information
- **Gap Analysis**: AI-powered analysis of gaps between user profile and program requirements
- **Action Plans**: Personalized improvement plans with actionable items
- **IELTS Training**: AI-powered writing feedback and speaking simulation
- **Authentication**: JWT + OAuth (Google, Email, Phone verification)
- **Payment Integration**: Stripe for premium features

## Tech Stack

## Tech Stack

### Frontend
- **Next.js 14** - React framework (App Router)
- **TypeScript** - Type safety
- **TailwindCSS** - Styling framework

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11+** - Programming language
- **JWT** - Authentication
- **Google OAuth** - Third-party login



**Databases**:
- PostgreSQL (relational data)
- Qdrant (vector database)
- Redis (cache & sessions)
- SQLAlchemy - ORM
- Alembic - Database migrations

**AI/LLM**: Agentic RAG with OpenAI/Anthropic API

**Payment**: Stripe

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+


### Manual Setup (Alternative)
### Using Docker Compose (Recommended)

1. **Clone the project and enter the directory**
   ```bash
   cd ai-school-recommendation-system
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file and fill in your configuration (especially JWT_SECRET_KEY and Google OAuth configuration)
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Development

1. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   Copy the example file and edit:
   ```bash
   cp .env.example .env
   ```
   
   Edit `backend/.env` and fill in actual configuration (especially `GOOGLE_CLIENT_ID`):
   ```bash
   # Database configuration
   DATABASE_URL=postgresql://postgres:postgres@localhost:5433/logindb
   
   # JWT configuration
   JWT_SECRET_KEY=your-secret-key-change-in-production
   
   # Google OAuth configuration
   GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

3. **Start PostgreSQL and Redis** (using Docker Compose)
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start backend service**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables**
   Copy the example file and edit:
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `frontend/.env.local` and fill in actual configuration:
   ```bash
   # API configuration
   NEXT_PUBLIC_API_URL=http://localhost:8000
   
   # Google OAuth configuration (optional, will be automatically fetched from backend if backend is configured)
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

## Google OAuth Configuration

### Basic Configuration Steps

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing project
3. Enable **Google Identity Services API**
4. Create OAuth 2.0 Client ID:
   - Application type: **Web application**
5. Copy the generated Client ID (format: `xxx.apps.googleusercontent.com`)

### Environment Variable Configuration

**Backend Configuration** (`backend/.env`):
```bash
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Frontend Configuration** (`frontend/.env.local`, optional):
```bash
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

> **Note**: If the backend has configured `GOOGLE_CLIENT_ID`, the frontend will automatically fetch it from the backend API, so there's no need to configure the frontend environment variable separately.

### Debugging and Testing


1. **API endpoints**:
   

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/google` - Google login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user information
- `GET /api/auth/config` - Check Google OAuth configuration status
- `POST /api/auth/google/test` - Test Google token verification (does not create user)
- `POST /api/auth/google` - Complete Google login flow



## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Development Notes

### Backend Module Structure

- `auth/` - Authentication related functionality
  - `models.py` - User model
  - `schemas.py` - API request/response schemas
  - `service.py` - Business logic
  - `routes.py` - API routes
  - `jwt.py` - JWT utility functions
  - `oauth.py` - OAuth handling

- `profile/` - User profile management
  - `models.py` - User profile model
  - `schemas.py` - API schemas
  - `service.py` - Business logic
  - `routes.py` - API routes

### Frontend Page Structure

- `app/(auth)/` - Authentication pages (login, register)
- `app/dashboard/` - User center (profile, settings)

## Future Extensions

The system has reserved directory structures for the following modules:

- `school/` - School data management
- `recommendation/` - School recommendation
- `gap_analysis/` - Gap analysis
- `feedback/` - Feedback system
- `ielts_training/` - IELTS training
- `llm_proxy/` - LLM proxy

## License

MIT
