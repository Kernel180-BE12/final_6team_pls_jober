# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a full-stack application with three main services:
- **Frontend**: Vue 3 + TypeScript + Vuetify (port 3000)
- **Backend**: Spring Boot + MySQL + Redis (port 8080)  
- **AI Service**: FastAPI + ChromaDB + OpenAI + HuggingFace (port 8000)

## Development Commands

### Frontend (Vue 3)
```bash
cd front
npm install                 # Install dependencies
npm run dev                 # Start development server (port 3000)
npm run build              # Build for production
npm run type-check         # Run TypeScript type checking
npm run lint               # Run ESLint with auto-fix
npm run format             # Format code with Prettier
```

### Backend (Spring Boot)
```bash
cd back
chmod +x gradlew           # Set permissions (Linux/Mac only)
./gradlew build           # Build the project
./gradlew bootRun         # Run development server (port 8080)
./gradlew test            # Run unit tests
./gradlew integrationTest # Run integration tests
```

### AI Service (FastAPI)
```bash
cd ai
python -m venv venv                              # Create virtual environment
venv\Scripts\activate                            # Activate (Windows)
source venv/bin/activate                         # Activate (Linux/Mac)
pip install -r requirements.txt                 # Install dependencies
uvicorn main:app --reload --host 0.0.0.0 --port 8000  # Run server
python -m pytest                                # Run tests
```

### Startup Scripts
```bash
# Start all services at once
./start_all.sh    # Linux/Mac
start_all.bat     # Windows
```

## Architecture & Structure

### Frontend Architecture
- **Framework**: Vue 3 Composition API with TypeScript
- **UI Library**: Vuetify (Material Design)
- **State Management**: Pinia stores
- **HTTP Client**: Axios with @tanstack/vue-query
- **Build Tool**: Vite with hot reload
- **Routing**: Vue Router with lazy loading
- **Proxy**: Automatic proxying `/api/*` → Backend, `/ai/*` → AI Service

### Backend Architecture
- **Framework**: Spring Boot 3.2.0 with Java 17
- **Security**: Spring Security with JWT authentication  
- **Database**: MySQL with JPA/Hibernate ORM
- **Migration**: Flyway for database versioning
- **Cache**: Redis for session storage and caching
- **API**: RESTful endpoints under `/api` context path
- **Build**: Gradle with Wrapper

### AI Service Architecture
- **Framework**: FastAPI with async/await support
- **AI Integration**: 
  - OpenAI API for chat and embeddings
  - HuggingFace for open-source models
  - ChromaDB for vector database operations
  - LangChain for advanced AI workflows
- **Template System**: Alimtalk template validation service
- **Models**: Pydantic for request/response validation

## Service Communication

### API Endpoints Structure
- Frontend (`http://localhost:3000`)
  - Proxies `/api/*` → Backend (`http://localhost:8080/api/*`)
  - Proxies `/ai/*` → AI Service (`http://localhost:8000/ai/*`)

### Backend API Routes
- `GET /api/` - Home endpoint
- `GET /api/health` - Health check
- `POST /api/auth/login` - User authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/pw/request` - Password reset request
- `POST /api/auth/pw/reset` - Password reset
- `GET /api/users` - User management
- Template and account management endpoints

### AI Service Routes  
- `GET /health` - Health check
- `POST /ai/openai/chat` - OpenAI chat completion
- `POST /ai/chromadb/documents` - ChromaDB operations
- `POST /ai/huggingface/generate` - HuggingFace model inference
- `POST /ai/alimtalk/validate` - Alimtalk template validation
- `POST /ai/template/generate` - Template generation endpoint

## Environment Setup

### Required Services
- **Java 17+** for Spring Boot backend
- **Node.js 18+** for Vue frontend  
- **Python 3.8+** for FastAPI AI service
- **MySQL** database server
- **Redis** cache server

### Environment Variables
Create `.env` files in respective directories:

**Backend** (`back/.env`):
```env
DB_URL=jdbc:mysql://localhost:3306/final_project?serverTimezone=UTC&characterEncoding=UTF-8
DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
DB_DRIVER=com.mysql.cj.jdbc.Driver
REDIS_PASSWORD=your_redis_password  
JWT_SECRET=your-jwt-secret-key-here-make-it-at-least-64-characters-long-for-security
```

**AI Service** (`ai/.env`):
```env
OPENAI_API_KEY=your_openai_api_key_here
HF_TOKEN=your_huggingface_token_here
```

## Testing Strategy

### Frontend Testing
- TypeScript compilation via `npm run type-check`
- ESLint for code quality via `npm run lint`
- Prettier formatting via `npm run format`
- Manual testing through development server

### Backend Testing
- Unit tests with JUnit via `./gradlew test`
- Integration tests via `./gradlew integrationTest`
- API testing with curl commands provided in README
- Database migration testing with Flyway

### AI Service Testing
- pytest for unit tests via `python -m pytest`
- API validation through FastAPI's automatic OpenAPI docs at `/docs`
- Test scripts available: `updated_test.py`, `multiple_test.py`

## Development Workflow

### Starting Full System
1. **Database Setup**: Ensure MySQL and Redis are running
2. **Environment Variables**: Configure `.env` files in respective directories
3. **Backend**: `cd back && ./gradlew bootRun` 
4. **AI Service**: `cd ai && uvicorn main:app --reload`
5. **Frontend**: `cd front && npm run dev`
6. **Access**: Navigate to `http://localhost:3000`

### Quick Start (All Services)
```bash
# Use the provided startup script
./start_all.sh    # Linux/Mac
start_all.bat     # Windows
```

### Making Changes
- Frontend changes auto-reload via Vite
- Backend changes require restart unless using Spring DevTools
- AI service auto-reloads with `--reload` flag
- Database schema changes handled by Flyway migrations

### Build Process
- Frontend: Vite builds to `dist/` directory
- Backend: Gradle builds JAR to `build/libs/`
- AI Service: Python dependencies via requirements.txt

## Common Issues & Solutions

### Port Conflicts
- Frontend: Use `npm run dev -- --port 3001`
- Backend: Modify `application.yml` server port
- AI Service: Use `uvicorn main:app --port 8001`

### Database Connection Issues  
- Verify MySQL service is running
- Check credentials in `.env` file
- Confirm database `final_project` exists
- Ensure proper character set: `utf8mb4`

### AI Service Dependencies
- Large models download on first use (HuggingFace)
- ChromaDB creates `./chroma_db` directory for persistence
- GPU acceleration available with CUDA installation
- Virtual environment must be activated

### Build Issues
- Java 17+ required for backend
- Node.js 18+ required for frontend  
- Python 3.8+ required for AI service
- Gradle wrapper permissions: `chmod +x gradlew`

## Authentication System

### Current Implementation
- **JWT-based authentication** with access and refresh tokens
- **BCrypt password hashing** for secure storage
- **Password reset system** with UUID tokens (30min validity)
- **User registration** with email/username validation
- **Role-based access control** (USER role default)

### Database Schema
- **Account Entity**: `account_id`, `user_name`, `email`, `password_hash`, `phone_number`, `role`, `status`, `company_name`, `biz_reg_no`, `created_at`, `updated_at`
- **PasswordResetToken Entity**: `token`, `account_id`, `expiry_date`

### Token Configuration
- **Access Token**: 1 hour expiration
- **Refresh Token**: 7 days expiration
- **Redis Integration**: Session storage and token management

## Database Configuration
- **Remote Server**: `134.185.106.160:3306`
- **Database**: `final_project`
- **Character Set**: `utf8mb4_unicode_ci`
- **Migration Tool**: Flyway with baseline support
- **ORM**: JPA/Hibernate with MySQL8Dialect

## Docker Support
- **Docker Compose**: Available in `Docker/docker-compose.yml`
- **Redis Configuration**: Custom redis.conf and Dockerfile
- **Container Orchestration**: Full stack deployment support