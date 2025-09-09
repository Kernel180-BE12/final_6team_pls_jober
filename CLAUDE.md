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
python -m build                                 # Build package (requires setup.py)
```

## Architecture & Structure

### Frontend Architecture
- **Framework**: Vue 3 Composition API with TypeScript
- **UI Library**: Vuetify (Material Design)
- **State Management**: Pinia stores
- **HTTP Client**: Axios with automatic proxy to backend services
- **Build Tool**: Vite with hot reload
- **Routing**: Vue Router with lazy loading

### Backend Architecture
- **Framework**: Spring Boot 3.2.0 with Java 17
- **Security**: Spring Security with JWT authentication
- **Database**: MySQL with JPA/Hibernate ORM
- **Cache**: Redis for session storage
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
- `GET /api/users` - User management
- Template and account management endpoints

### AI Service Routes  
- `GET /health` - Health check
- `POST /ai/openai/chat` - OpenAI chat completion
- `POST /ai/chromadb/documents` - ChromaDB operations
- `POST /ai/huggingface/generate` - HuggingFace model inference
- `POST /ai/alimtalk/validate` - Alimtalk template validation

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
```
DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password  
JWT_SECRET=your-jwt-secret-key-here
```

**AI Service** (`ai/.env`):
```
OPENAI_API_KEY=your_openai_api_key_here
HF_TOKEN=your_huggingface_token_here
```

## Testing Strategy

### Frontend Testing
- TypeScript compilation via `npm run type-check`
- ESLint for code quality via `npm run lint`
- Manual testing through development server

### Backend Testing
- Unit tests with JUnit via `./gradlew test`
- Integration tests via `./gradlew integrationTest`
- API testing with curl commands provided in README

### AI Service Testing
- pytest for unit tests via `python -m pytest`
- API validation through FastAPI's automatic OpenAPI docs at `/docs`
- Test scripts available: `updated_test.py`, `multiple_test.py`

## Development Workflow

### Starting Full System
1. **Database Setup**: Ensure MySQL and Redis are running
2. **Backend**: `cd back && ./gradlew bootRun` 
3. **AI Service**: `cd ai && uvicorn main:app --reload`
4. **Frontend**: `cd front && npm run dev`
5. **Access**: Navigate to `http://localhost:3000`

### Making Changes
- Frontend changes auto-reload via Vite
- Backend changes require restart unless using Spring DevTools
- AI service auto-reloads with `--reload` flag
- Database schema changes need migration through JPA

### Build Process
- Frontend: Vite builds to `dist/` directory
- Backend: Gradle builds JAR to `build/libs/`
- AI Service: Python build creates wheel/tar.gz in `dist/`

## Common Issues & Solutions

### Port Conflicts
- Frontend: Use `npm run dev -- --port 3001`
- Backend: Modify `application.properties` server port
- AI Service: Use `uvicorn main:app --port 8001`

### Database Connection Issues  
- Verify MySQL service is running
- Check credentials in `.env` file
- Confirm database `final_project` exists

### AI Service Dependencies
- Large models download on first use (HuggingFace)
- ChromaDB creates `./chroma_db` directory for persistence
- GPU acceleration available with CUDA installation