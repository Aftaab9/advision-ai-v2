# 🚀 Setup Instructions - AdVision AI

**Quick start guide to get AdVision AI running locally**

---

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Docker Desktop installed
- Git installed

### Steps

```bash
# 1. Clone repository
git clone https://github.com/Aftaab9/advision-ai-v2.git
cd advision-ai-v2

# 2. Create environment file
cp backend/.env.example backend/.env

# 3. Edit backend/.env (optional - works without API keys)
# Add your API keys if you have them:
# - GROQ_API_KEY (for chatbot)
# - R2_ACCESS_KEY_ID & R2_SECRET_ACCESS_KEY (for file uploads)

# 4. Start all services
docker-compose up --build

# 5. In a new terminal, run migrations
docker-compose exec backend alembic upgrade head

# 6. Open browser
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

**That's it! You're ready to go! 🎉**

---

## 📋 Detailed Setup

### 1. Install Prerequisites

#### Docker Desktop
- **Windows/Mac**: Download from [docker.com](https://www.docker.com/products/docker-desktop)
- **Linux**: 
  ```bash
  sudo apt-get update
  sudo apt-get install docker.io docker-compose
  ```

#### Git
- **Windows**: Download from [git-scm.com](https://git-scm.com/)
- **Mac**: `brew install git`
- **Linux**: `sudo apt-get install git`

### 2. Clone Repository

```bash
git clone https://github.com/Aftaab9/advision-ai-v2.git
cd advision-ai-v2
```

### 3. Environment Configuration

#### Backend Environment
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```env
# Database (auto-configured by Docker)
DATABASE_URL=postgresql://advision:advision_dev_password@db:5432/advision

# JWT Secret (change in production!)
JWT_SECRET=your-secret-key-change-in-production

# Optional: Groq API (for chatbot)
GROQ_API_KEY=your-groq-api-key-here

# Optional: Cloudflare R2 (for file uploads)
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=advision-creatives
R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com

# Optional: HuggingFace (for ML models)
HUGGINGFACE_TOKEN=your-hf-token

# Chroma DB
CHROMA_HOST=chroma
CHROMA_PORT=8000

# ML Service
ML_SERVICE_URL=http://ml-service:8001
```

#### Frontend Environment
```bash
cd frontend
```

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Start Services

#### Option A: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Option B: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**ML Service:**
```bash
cd ml-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
```bash
# Install PostgreSQL locally
# Create database: advision
# Update DATABASE_URL in .env
```

**Chroma:**
```bash
docker run -p 8002:8000 ghcr.io/chroma-core/chroma:latest
```

### 5. Run Database Migrations

```bash
# If using Docker Compose
docker-compose exec backend alembic upgrade head

# If running locally
cd backend
alembic upgrade head
```

### 6. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Next.js web app |
| **Backend API** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **ML Service** | http://localhost:8001 | ML API |
| **Chroma DB** | http://localhost:8002 | Vector database |
| **PostgreSQL** | localhost:5432 | Database |

---

## 🔑 Getting API Keys (Optional)

### Groq API (for Chatbot)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Create API key
4. Add to `backend/.env`: `GROQ_API_KEY=your-key`
5. **FREE**: 14,400 requests/day

### Cloudflare R2 (for File Uploads)
1. Go to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Create R2 bucket
3. Generate API tokens
4. Add to `backend/.env`:
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`
   - `R2_ENDPOINT_URL`
5. **FREE**: 10GB storage

### HuggingFace (for ML Models)
1. Go to [huggingface.co](https://huggingface.co)
2. Sign up for free account
3. Create access token
4. Add to `backend/.env`: `HUGGINGFACE_TOKEN=your-token`
5. **FREE**: Inference API

---

## 🧪 Testing

### Create Test User

```bash
# Using API docs (http://localhost:8000/docs)
# 1. Go to POST /auth/register
# 2. Click "Try it out"
# 3. Enter:
{
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User",
  "organization_name": "Test Org"
}
# 4. Execute
# 5. Copy the access_token
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get campaigns (with token)
curl http://localhost:8000/campaigns/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Run Backend Tests

```bash
# If using Docker
docker-compose exec backend pytest

# If running locally
cd backend
pytest
```

---

## 🐛 Troubleshooting

### Frontend Errors (Red Squiggles)

**Problem**: TypeScript errors in frontend files  
**Solution**: Install npm packages

```bash
cd frontend
npm install
```

The errors will disappear once packages are installed.

### Docker Issues

**Problem**: Port already in use  
**Solution**: Stop conflicting services

```bash
# Check what's using port 3000
lsof -i :3000  # Mac/Linux
netstat -ano | findstr :3000  # Windows

# Kill process or change port in docker-compose.yml
```

**Problem**: Docker build fails  
**Solution**: Clean Docker cache

```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Database Issues

**Problem**: Migration fails  
**Solution**: Reset database

```bash
docker-compose down -v
docker-compose up -d db
docker-compose exec backend alembic upgrade head
```

**Problem**: Connection refused  
**Solution**: Wait for database to be ready

```bash
# Check database health
docker-compose ps
docker-compose logs db

# Wait 10 seconds after starting, then run migrations
```

### Chroma Issues

**Problem**: Chroma connection fails  
**Solution**: Check Chroma is running

```bash
docker-compose ps chroma
docker-compose logs chroma

# Restart Chroma
docker-compose restart chroma
```

---

## 📦 Package Installation

### Frontend Dependencies

```bash
cd frontend
npm install

# Or with specific versions
npm install next@14.2.0 react@18.2.0 react-dom@18.2.0
npm install axios recharts lucide-react js-cookie date-fns
npm install -D typescript @types/node @types/react @types/react-dom
npm install -D tailwindcss postcss autoprefixer
```

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt

# Or install individually
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary
pip install python-jose passlib bcrypt python-dotenv
pip install pydantic pydantic-settings email-validator
pip install httpx aiohttp pandas numpy
pip install chromadb boto3 pytest
```

---

## 🚀 Next Steps

1. **Register a user** at http://localhost:3000/register
2. **Login** at http://localhost:3000/login
3. **Create a campaign** in the dashboard
4. **Upload documents** for RAG
5. **Chat with AI** assistant
6. **Explore API docs** at http://localhost:8000/docs

---

## 📚 Additional Resources

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [API Documentation](http://localhost:8000/docs)
- [Project Summary](PROJECT_SUMMARY.md)
- [Status Tracking](STATUS.md)

---

## 💡 Tips

1. **Use Docker Compose** - Easiest way to run everything
2. **Check logs** - `docker-compose logs -f` to debug issues
3. **API docs** - Use Swagger UI to test endpoints
4. **Hot reload** - Code changes auto-reload in dev mode
5. **Environment variables** - Don't commit `.env` files!

---

## 🆘 Need Help?

1. Check [STATUS.md](STATUS.md) for current progress
2. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture
3. Check Docker logs: `docker-compose logs -f`
4. Verify services are running: `docker-compose ps`
5. Restart services: `docker-compose restart`

---

**Happy coding! 🎉**
