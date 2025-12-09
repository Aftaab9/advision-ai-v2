# 🔧 Docker Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: Docker Build Taking Too Long

**Symptom:** `docker-compose build` runs for several minutes

**Solution:** This is NORMAL for first build! Docker is:
1. Downloading Python base image (~150MB)
2. Installing system packages (gcc, postgresql-client)
3. Installing Python dependencies (~100+ packages)
4. Building frontend (Node.js packages)

**Expected Time:** 5-10 minutes for first build

**What to do:** Let it complete! Subsequent builds will be much faster (cached).

---

### Issue 2: Port Already in Use

**Error:** `Error: Port 8000 is already in use`

**Solution:**
```bash
# Stop all Docker containers
docker-compose down

# Or change ports in docker-compose.yml
# Change 8000:8000 to 8080:8000 (for backend)
# Change 3000:3000 to 3001:3000 (for frontend)
```

---

### Issue 3: Database Connection Failed

**Error:** `could not connect to server`

**Solution:**
```bash
# Wait for database to be ready (takes 10-15 seconds)
# Check database status
docker-compose ps

# If db is not healthy, restart
docker-compose restart db

# Wait 15 seconds, then run migrations
docker-compose exec backend alembic upgrade head
```

---

### Issue 4: Out of Memory / Disk Space

**Error:** `no space left on device` or build crashes

**Solution:**
```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk space
docker system df
```

---

### Issue 5: Frontend Build Fails

**Error:** `npm ERR!` or `Module not found`

**Solution:**
```bash
# Rebuild frontend only
docker-compose build --no-cache frontend

# Or install locally first
cd frontend
npm install
cd ..
```

---

## Alternative: Run Without Docker

If Docker is too slow, run services locally:

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (New Terminal)
```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

### 3. Database (Use SQLite Instead)
Edit `backend/.env`:
```
DATABASE_URL=sqlite:///./advision.db
```

Then run migrations:
```bash
cd backend
alembic upgrade head
```

---

## Quick Commands

### Start Everything
```bash
docker-compose up --build
```

### Start in Background
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Everything
```bash
docker-compose down
```

### Clean Restart
```bash
docker-compose down -v
docker-compose up --build
```

### Check Status
```bash
docker-compose ps
```

---

## Performance Tips

### 1. Increase Docker Resources
- Docker Desktop → Settings → Resources
- RAM: 4GB minimum (8GB recommended)
- CPU: 2 cores minimum (4 recommended)
- Disk: 20GB minimum

### 2. Use BuildKit (Faster Builds)
```bash
# Windows PowerShell
$env:DOCKER_BUILDKIT=1
$env:COMPOSE_DOCKER_CLI_BUILD=1

# Then build
docker-compose build
```

### 3. Build Services Separately
```bash
# Build one at a time
docker-compose build db
docker-compose build backend
docker-compose build ml-service
docker-compose build frontend
docker-compose build chroma
```

---

## Still Having Issues?

### Check Docker Installation
```bash
docker --version
docker-compose --version
```

Should show:
- Docker: 20.10+ or newer
- Docker Compose: 2.0+ or newer

### Check Docker is Running
```bash
docker ps
```

Should NOT show error. If it does, start Docker Desktop.

### Test Simple Container
```bash
docker run hello-world
```

Should download and run successfully.

---

## Contact & Support

If none of these solutions work:

1. Share the EXACT error message
2. Share output of `docker-compose ps`
3. Share output of `docker-compose logs backend`
4. Check Docker Desktop logs

---

**Remember:** First build is SLOW (5-10 min). This is normal! ☕

