# 🚀 Cloudflare R2 Setup Guide (10 Minutes)

**Why R2?** FREE 10GB storage + NO egress fees (saves $$$ at scale)

---

## 📋 Step-by-Step Setup

### Step 1: Create Cloudflare Account (2 minutes)

1. Go to: **https://dash.cloudflare.com**
2. Click **"Sign Up"**
3. Enter your email and password
4. Verify your email
5. **No credit card required!** ✅

---

### Step 2: Enable R2 (1 minute)

1. In Cloudflare dashboard, click **"R2"** in left sidebar
2. Click **"Purchase R2 Plan"**
3. Select **"Free"** plan (10GB storage, 10M reads/month)
4. Click **"Proceed"**
5. Done! R2 is now enabled ✅

---

### Step 3: Create R2 Bucket (2 minutes)

1. Click **"Create bucket"**
2. Enter bucket name: **`advision-creatives`**
3. Select location: **Automatic** (recommended)
4. Click **"Create bucket"**
5. Done! Bucket created ✅

---

### Step 4: Get API Credentials (5 minutes)

#### 4.1 Create API Token

1. Click **"Manage R2 API Tokens"** (top right)
2. Click **"Create API token"**
3. Enter token name: **`advision-api-token`**
4. Permissions:
   - ✅ **Object Read & Write**
   - ✅ **Bucket Read & Write** (optional)
5. TTL: **Forever** (or set expiry)
6. Click **"Create API Token"**

#### 4.2 Copy Credentials

You'll see 3 important values:

```
Access Key ID: 1234567890abcdef1234567890abcdef
Secret Access Key: abcdef1234567890abcdef1234567890abcdef1234567890
Endpoint URL: https://1234567890abcdef.r2.cloudflarestorage.com
```

**⚠️ IMPORTANT:** Copy these NOW! You won't see the Secret Access Key again!

---

### Step 5: Add to Your Project (1 minute)

1. Open `advision-ai-v2/backend/.env`
2. Add your credentials:

```env
# Cloudflare R2 Configuration
R2_ACCESS_KEY_ID=1234567890abcdef1234567890abcdef
R2_SECRET_ACCESS_KEY=abcdef1234567890abcdef1234567890abcdef1234567890
R2_BUCKET_NAME=advision-creatives
R2_ENDPOINT_URL=https://1234567890abcdef.r2.cloudflarestorage.com
```

3. Save the file
4. Done! ✅

---

## 🧪 Test Your Setup

### Option 1: Using Python (Quick Test)

```python
import boto3

# Your R2 credentials
s3 = boto3.client(
    's3',
    endpoint_url='https://1234567890abcdef.r2.cloudflarestorage.com',
    aws_access_key_id='your-access-key-id',
    aws_secret_access_key='your-secret-access-key'
)

# Test: List buckets
buckets = s3.list_buckets()
print("Buckets:", [b['Name'] for b in buckets['Buckets']])

# Test: Upload file
s3.put_object(
    Bucket='advision-creatives',
    Key='test.txt',
    Body=b'Hello from AdVision AI!'
)
print("✅ Upload successful!")

# Test: Download file
obj = s3.get_object(Bucket='advision-creatives', Key='test.txt')
print("Content:", obj['Body'].read().decode())
```

### Option 2: Using Your App

```bash
# Start your backend
cd advision-ai-v2
docker-compose up backend

# Go to API docs
# http://localhost:8000/docs

# Try the upload endpoint:
# POST /creatives/upload/{campaign_id}
```

---

## 📊 R2 Free Tier Limits

| Feature | Free Tier | Notes |
|---------|-----------|-------|
| **Storage** | 10 GB | ~10,000 images |
| **Class A Operations** | 1M/month | Writes, lists |
| **Class B Operations** | 10M/month | Reads |
| **Egress** | **FREE** | No bandwidth charges! |

**Perfect for MVP!** ✅

---

## 🔧 Troubleshooting

### Error: "Access Denied"
**Solution:** Check your API token has "Object Read & Write" permissions

### Error: "Bucket not found"
**Solution:** Make sure bucket name matches exactly: `advision-creatives`

### Error: "Invalid endpoint"
**Solution:** Endpoint URL should be: `https://[account-id].r2.cloudflarestorage.com`

### Error: "Signature mismatch"
**Solution:** Check your Secret Access Key is correct (no extra spaces)

---

## 🎯 Quick Reference

### Your R2 Configuration

```env
# Copy these to backend/.env
R2_ACCESS_KEY_ID=<your-access-key-id>
R2_SECRET_ACCESS_KEY=<your-secret-access-key>
R2_BUCKET_NAME=advision-creatives
R2_ENDPOINT_URL=https://<your-account-id>.r2.cloudflarestorage.com
```

### Important URLs

- **Dashboard:** https://dash.cloudflare.com
- **R2 Console:** https://dash.cloudflare.com/r2
- **API Tokens:** https://dash.cloudflare.com/profile/api-tokens
- **Documentation:** https://developers.cloudflare.com/r2/

---

## 💡 Pro Tips

1. **Use unique filenames** - Add UUID to prevent overwrites
2. **Set CORS** - If accessing from browser directly
3. **Enable versioning** - For backup (optional)
4. **Monitor usage** - Check dashboard monthly
5. **Use CDN** - Cloudflare CDN is automatic!

---

## 🚀 Next Steps

1. ✅ Create Cloudflare account
2. ✅ Enable R2
3. ✅ Create bucket
4. ✅ Get API credentials
5. ✅ Add to `.env` file
6. ✅ Test upload
7. ✅ Start building!

---

## 📞 Need Help?

- **Cloudflare Docs:** https://developers.cloudflare.com/r2/
- **Community:** https://community.cloudflare.com/
- **Support:** https://dash.cloudflare.com/support

---

**🎉 R2 Setup Complete! You now have FREE 10GB storage! 🎉**

**Total Time:** ~10 minutes  
**Total Cost:** ₹0 forever  
**Storage:** 10GB free  
**Egress:** FREE (no bandwidth charges)

**Perfect for your MVP!** ✅
