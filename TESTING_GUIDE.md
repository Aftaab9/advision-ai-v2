# 🧪 TESTING GUIDE - AdVision AI

**Complete testing checklist before deployment**

---

## 🚀 LOCAL TESTING (Before Deployment)

### Step 1: Start Services

```bash
cd advision-ai-v2
docker-compose up --build
```

Wait for all services to start:
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:3000
- ✅ ML Service: http://localhost:8001
- ✅ Chroma: http://localhost:8002
- ✅ PostgreSQL: localhost:5432

### Step 2: Run Migrations

```bash
# In new terminal
docker-compose exec backend alembic upgrade head
```

Expected output: `Running upgrade -> head`

---

## ✅ FEATURE TESTING CHECKLIST

### 1. Authentication (5 minutes)

**Register:**
- [ ] Go to http://localhost:3000/register
- [ ] Enter email, password, name
- [ ] Click "Create account"
- [ ] Should redirect to dashboard
- [ ] Check: JWT token in cookies

**Login:**
- [ ] Logout
- [ ] Go to http://localhost:3000/login
- [ ] Enter credentials
- [ ] Click "Sign in"
- [ ] Should redirect to dashboard

**Expected:** ✅ Auth works, tokens stored

---

### 2. Dashboard (3 minutes)

**Check Display:**
- [ ] Total campaigns count
- [ ] Total spend/revenue
- [ ] Average CTR/ROI
- [ ] Platform breakdown (Pie chart)
- [ ] Top campaigns (Bar chart)

**Expected:** ✅ Dashboard loads, charts render

---

### 3. Campaign Management (5 minutes)

**Create Campaign:**
- [ ] Click "New Campaign"
- [ ] Enter name: "Test Campaign"
- [ ] Select platform: Facebook
- [ ] Set budget: ₹10,000
- [ ] Set dates
- [ ] Click "Create"
- [ ] Should appear in list

**View Campaign:**
- [ ] Click on campaign
- [ ] Check metrics display
- [ ] ROI calculation correct

**Delete Campaign:**
- [ ] Click delete icon
- [ ] Confirm deletion
- [ ] Should disappear from list

**Expected:** ✅ CRUD operations work

---

### 4. File Upload - R2 (5 minutes)

**Upload Creative:**
- [ ] Go to campaign
- [ ] Click "Upload Creative"
- [ ] Select image (JPEG/PNG)
- [ ] Upload
- [ ] Check: File appears in list
- [ ] Check: Image URL from R2

**Test R2 Connection:**
```bash
# Check backend logs
docker-compose logs backend | grep "R2"
```

**Expected:** ✅ Files upload to R2, URLs work

---

### 5. AI Chatbot - Groq (5 minutes)

**Test Chat:**
- [ ] Go to http://localhost:3000/chat
- [ ] Type: "What is marketing analytics?"
- [ ] Press Enter
- [ ] Wait for response
- [ ] Check: Response from Llama 3.1 70B
- [ ] Check: Response time <3 seconds

**Test RAG:**
- [ ] Toggle "Use knowledge base (RAG)" ON
- [ ] Ask: "What campaigns do I have?"
- [ ] Check: Uses document context

**Test Quick Insights:**
- [ ] Click "Quick Insights"
- [ ] Check: AI analyzes campaigns
- [ ] Check: 3 actionable insights

**Expected:** ✅ Chatbot works, fast responses

---

### 6. RAG Document Q&A (5 minutes)

**Upload Document:**
- [ ] Go to http://localhost:3000/documents
- [ ] Click "Upload Document"
- [ ] Select .txt or .md file
- [ ] Upload
- [ ] Check: Document in list

**Query Documents:**
- [ ] Type query in search box
- [ ] Press Enter
- [ ] Check: Relevant results
- [ ] Check: Relevance scores
- [ ] Check: Document previews

**Expected:** ✅ RAG pipeline works, semantic search

---

### 7. Analytics (3 minutes)

**Dashboard Stats:**
- [ ] Check total campaigns
- [ ] Check spend/revenue
- [ ] Check ROI calculations
- [ ] Check platform breakdown

**ROI Metrics:**
- [ ] Go to analytics page
- [ ] Check ROI, CAC, CLV
- [ ] Check payback period

**Expected:** ✅ Analytics accurate

---

### 8. ML Predictions (3 minutes)

**Predict Engagement:**
- [ ] Go to campaign
- [ ] Click "Predict" icon
- [ ] Check: Engagement prediction
- [ ] Check: Prediction score

**Trust Score:**
- [ ] Upload creative
- [ ] Check: Trust score (0-100)
- [ ] Check: Badge level
- [ ] Check: Component scores

**Expected:** ✅ ML predictions work

---

## 🔧 API TESTING

### Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Get campaigns (with token)
curl http://localhost:8000/campaigns/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:** ✅ All endpoints respond correctly

---

## 🧪 AUTOMATED TESTS

### Run Backend Tests

```bash
# Run pytest
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app
```

**Expected:** ✅ All tests pass

---

## 📊 PERFORMANCE TESTING

### Load Testing

**Test Groq API:**
- Send 10 concurrent requests
- Check: All responses <3 seconds
- Check: No rate limit errors

**Test R2 Upload:**
- Upload 10 files simultaneously
- Check: All uploads succeed
- Check: No connection errors

**Test Database:**
- Create 100 campaigns
- Check: Query time <1 second
- Check: No connection pool errors

**Expected:** ✅ System handles load

---

## 🚨 ERROR TESTING

### Test Error Handling

**Invalid Login:**
- [ ] Try wrong password
- [ ] Check: Error message displayed
- [ ] Check: No crash

**Invalid File Upload:**
- [ ] Try uploading .exe file
- [ ] Check: Rejected with message
- [ ] Check: No crash

**Network Errors:**
- [ ] Stop backend
- [ ] Try API call from frontend
- [ ] Check: Error message
- [ ] Check: Graceful handling

**Expected:** ✅ Errors handled gracefully

---

## ✅ PRE-DEPLOYMENT CHECKLIST

Before deploying to production:

### Code Quality
- [ ] All features tested locally
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] All tests passing

### Configuration
- [ ] All API keys configured
- [ ] Environment variables set
- [ ] Database migrations ready
- [ ] .env files not in Git

### Documentation
- [ ] README updated
- [ ] API docs complete
- [ ] Deployment guide ready
- [ ] User guide created

### Security
- [ ] JWT secret changed
- [ ] API keys secured
- [ ] CORS configured
- [ ] Rate limiting enabled

### Performance
- [ ] Load tested
- [ ] Response times <3s
- [ ] No memory leaks
- [ ] Database optimized

---

## 🎯 PRODUCTION TESTING

After deployment:

### Smoke Tests
- [ ] Frontend loads
- [ ] Can register/login
- [ ] Can create campaign
- [ ] Chatbot responds
- [ ] File upload works

### Integration Tests
- [ ] Frontend ↔ Backend
- [ ] Backend ↔ Database
- [ ] Backend ↔ R2
- [ ] Backend ↔ Groq
- [ ] Backend ↔ Chroma

### User Acceptance
- [ ] Test with real users
- [ ] Collect feedback
- [ ] Fix critical bugs
- [ ] Monitor errors

---

## 📈 MONITORING

### What to Monitor

**Vercel (Frontend):**
- Page load times
- Error rates
- Bandwidth usage

**Render (Backend):**
- Response times
- Error rates
- Memory usage
- CPU usage

**Supabase (Database):**
- Query performance
- Connection pool
- Storage usage

**Groq (LLM):**
- Request count
- Response times
- Rate limits

**Cloudflare R2:**
- Storage usage
- Bandwidth
- Request count

---

## ✅ TESTING COMPLETE!

### Results Summary

- [ ] All features tested ✅
- [ ] All tests passing ✅
- [ ] Performance acceptable ✅
- [ ] Errors handled ✅
- [ ] Ready for deployment ✅

---

**🎉 READY TO DEPLOY TO PRODUCTION! 🎉**

**Next:** Follow `PRODUCTION_DEPLOYMENT.md`
