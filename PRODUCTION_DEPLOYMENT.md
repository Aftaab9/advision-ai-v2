# 🚀 PRODUCTION DEPLOYMENT GUIDE

**Deploy AdVision AI to production in 30 minutes**

---

## 📋 PRE-DEPLOYMENT CHECKLIST

✅ All APIs configured (Groq + R2)  
✅ Code tested locally  
✅ Database migrations ready  
✅ Environment variables documented  
✅ GitHub repository up to date  

**Status:** READY TO DEPLOY! 🎉

---

## 🎯 DEPLOYMENT STACK (100% FREE)

| Component | Provider | Cost | Time |
|-----------|----------|------|------|
| **Frontend** | Vercel | FREE | 5 min |
| **Backend** | Render | FREE | 10 min |
| **Database** | Supabase | FREE | 10 min |
| **Storage** | Cloudflare R2 | FREE | ✅ Done |
| **LLM** | Groq | FREE | ✅ Done |

**Total Time:** 25 minutes  
**Total Cost:** ₹0/month

---

## 🚀 STEP 1: Deploy Database (10 minutes)

### Supabase Setup

1. **Create Account**
   - Go to: https://supabase.com
   - Sign up with GitHub (recommended)
   - No credit card required

2. **Create Project**
   - Click "New Project"
   - Name: `advision-ai`
   - Database Password: Generate strong password
   - Region: Choose closest to you
   - Click "Create new project"
   - Wait 2 minutes for setup

3. **Get Connection String**
   - Go to Project Settings → Database
   - Copy "Connection string" (URI format)
   - Replace `[YOUR-PASSWORD]` with your password
   - Example: `postgresql://postgres:password@db.xxx.supabase.co:5432/postgres`

4. **Run Migrations**
   ```bash
   # Update DATABASE_URL in backend/.env
   DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
   
   # Run migrations
   cd backend
   alembic upgrade head
   ```

✅ **Database deployed!**

---

## 🚀 STEP 2: Deploy Backend (10 minutes)

### Render Setup

1. **Create Account**
   - Go to: https://render.com
   - Sign up with GitHub
   - No credit card required

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository: `advision-ai-v2`
   - Name: `advision-backend`
   - Region: Choose closest
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Docker`
   - Instance Type: **Free**

3. **Environment Variables**
   Click "Advanced" → Add environment variables:
   
   ```env
   DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
   JWT_SECRET=your-long-random-secret-key-change-this
   GROQ_API_KEY=your-groq-api-key-from-env-file
   R2_ACCESS_KEY_ID=374c345d71429448ba4576e8f81a15e0
   R2_SECRET_ACCESS_KEY=your-r2-secret-key
   R2_BUCKET_NAME=advision-ai
   R2_ENDPOINT_URL=https://374c345d71429448ba4576e8f81a15e0.r2.cloudflarestorage.com
   CHROMA_HOST=localhost
   CHROMA_PORT=8000
   ML_SERVICE_URL=http://localhost:8001
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build
   - Copy your backend URL: `https://advision-backend.onrender.com`

✅ **Backend deployed!**

---

## 🚀 STEP 3: Deploy Frontend (5 minutes)

### Vercel Setup

1. **Create Account**
   - Go to: https://vercel.com
   - Sign up with GitHub
   - No credit card required

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import `advision-ai-v2` from GitHub
   - Framework Preset: **Next.js**
   - Root Directory: `frontend`
   - Click "Deploy"

3. **Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add:
   ```env
   NEXT_PUBLIC_API_URL=https://advision-backend.onrender.com
   ```

4. **Redeploy**
   - Go to Deployments
   - Click "..." → "Redeploy"
   - Wait 2 minutes

5. **Get URL**
   - Copy your frontend URL: `https://advision-ai-v2.vercel.app`

✅ **Frontend deployed!**

---

## 🧪 STEP 4: Test Production (5 minutes)

### Test Checklist

1. **Frontend Access**
   - Visit: `https://advision-ai-v2.vercel.app`
   - Should load login page ✅

2. **Register Account**
   - Click "Sign up"
   - Create test account
   - Should redirect to dashboard ✅

3. **Test Features**
   - ✅ Dashboard loads with charts
   - ✅ Create campaign
   - ✅ Upload creative (R2)
   - ✅ Chat with AI (Groq)
   - ✅ Upload document (RAG)
   - ✅ Query documents

4. **Check API**
   - Visit: `https://advision-backend.onrender.com/docs`
   - Should show Swagger UI ✅

✅ **All tests passed!**

---

## 🔧 POST-DEPLOYMENT

### 1. Update GitHub README

Add production URLs:
```markdown
## 🌐 Live Demo

- **Frontend:** https://advision-ai-v2.vercel.app
- **Backend API:** https://advision-backend.onrender.com
- **API Docs:** https://advision-backend.onrender.com/docs
```

### 2. Monitor Services

**Vercel Dashboard:**
- Analytics: https://vercel.com/dashboard
- Logs: Real-time deployment logs
- Metrics: Bandwidth, requests

**Render Dashboard:**
- Metrics: https://dashboard.render.com
- Logs: Real-time application logs
- Health: Auto-health checks

**Supabase Dashboard:**
- Database: https://supabase.com/dashboard
- SQL Editor: Run queries
- Logs: Database logs

### 3. Set Up Custom Domain (Optional)

**Vercel (Frontend):**
1. Go to Project Settings → Domains
2. Add your domain: `advision.yourdomain.com`
3. Update DNS records
4. SSL auto-configured ✅

**Render (Backend):**
1. Go to Settings → Custom Domain
2. Add: `api.yourdomain.com`
3. Update DNS records
4. SSL auto-configured ✅

---

## 📊 PRODUCTION COSTS

### Free Tier Limits

**Vercel:**
- Bandwidth: 100GB/month
- Builds: Unlimited
- Deployments: Unlimited
- **Cost:** FREE ✅

**Render:**
- Hours: 750/month (always on)
- Memory: 512MB
- CPU: Shared
- **Cost:** FREE ✅

**Supabase:**
- Database: 500MB
- Storage: 1GB
- API Requests: Unlimited
- **Cost:** FREE ✅

**Cloudflare R2:**
- Storage: 10GB
- Reads: 10M/month
- Writes: 1M/month
- **Cost:** FREE ✅

**Groq:**
- Requests: 14,400/day
- Model: Llama 3.1 70B
- **Cost:** FREE ✅

**Total Monthly Cost: ₹0** 🎉

---

## 🚨 TROUBLESHOOTING

### Frontend Issues

**Problem:** API calls failing  
**Solution:** Check `NEXT_PUBLIC_API_URL` in Vercel env vars

**Problem:** Build fails  
**Solution:** Run `npm install` locally, commit package-lock.json

### Backend Issues

**Problem:** Database connection fails  
**Solution:** Check DATABASE_URL format and password

**Problem:** R2 uploads fail  
**Solution:** Verify R2 credentials in Render env vars

**Problem:** Groq API fails  
**Solution:** Check GROQ_API_KEY is correct

### Database Issues

**Problem:** Migrations fail  
**Solution:** Run migrations manually:
```bash
DATABASE_URL=your-supabase-url alembic upgrade head
```

---

## 🎯 SCALING (When You Grow)

### When to Upgrade

**Vercel (Frontend):**
- Free: 100GB bandwidth
- Pro ($20/month): 1TB bandwidth
- Upgrade when: >100GB/month

**Render (Backend):**
- Free: 750 hours, 512MB RAM
- Starter ($7/month): Always on, 512MB RAM
- Upgrade when: Need 24/7 uptime

**Supabase (Database):**
- Free: 500MB, 50K users
- Pro ($25/month): 8GB, 100K users
- Upgrade when: >500MB data

**Cloudflare R2:**
- Free: 10GB storage
- Paid: $0.015/GB/month
- Upgrade when: >10GB files

**Groq:**
- Free: 14,400 req/day
- Contact for pricing
- Upgrade when: >14,400 req/day

---

## ✅ DEPLOYMENT COMPLETE!

### Your Production URLs

```
Frontend: https://advision-ai-v2.vercel.app
Backend: https://advision-backend.onrender.com
API Docs: https://advision-backend.onrender.com/docs
Database: Supabase (managed)
Storage: Cloudflare R2 (managed)
```

### What's Live

✅ Full-stack SaaS platform  
✅ AI Chatbot (Groq)  
✅ File uploads (R2)  
✅ RAG document Q&A  
✅ Analytics dashboard  
✅ Multi-tenant architecture  
✅ 100% FREE hosting  

### Next Steps

1. Share your app with users
2. Collect feedback
3. Monitor usage
4. Scale when needed

---

**🎉 CONGRATULATIONS! YOUR APP IS LIVE! 🎉**

**Total Time:** 25 minutes  
**Total Cost:** ₹0/month  
**Status:** ✅ PRODUCTION READY

**Share your app:** `https://advision-ai-v2.vercel.app`
