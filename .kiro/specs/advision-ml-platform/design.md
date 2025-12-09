# Design Document

## Overview

AdVision AI is a cloud-native, multi-tenant SaaS platform built on AWS that provides marketing intelligence through deep learning. The system architecture follows a microservices pattern with three primary services: a Next.js frontend, a FastAPI backend for business logic, and a dedicated ML inference service. The platform uses PostgreSQL (RDS) for transactional data, S3 for creative assets and model artifacts, and implements JWT-based authentication with organization-level data isolation.

The design addresses 8 critical ML gaps in marketing technology through specialized model components: CLIP-based semantic relevance scoring, emotion classification using fine-tuned transformers, LSTM-based ad fatigue prediction, GNN-powered bot detection, LLM-driven creative generation, temporal attribution modeling, CNN-based creative quality scoring, and fairness-aware bias auditing with explainable AI.

Given AWS Learner Lab constraints (limited services, no persistent resources), the design prioritizes a containerized deployment on a single EC2 instance with Docker Compose for development, with a clear migration path to ECS Fargate for production. All components are designed to be stateless where possible, with data persistence in RDS and S3.

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud (VPC)                          │
│                                                                   │
│  ┌────────────────┐                                              │
│  │   CloudFront   │ (Optional CDN for frontend assets)           │
│  │   (Optional)   │                                              │
│  └────────┬───────┘                                              │
│           │                                                       │
│  ┌────────▼────────────────────────────────────────────┐        │
│  │              EC2 Instance (t3.medium)               │        │
│  │                                                      │        │
│  │  ┌──────────────────────────────────────────────┐  │        │
│  │  │         Docker Compose Stack                 │  │        │
│  │  │                                              │  │        │
│  │  │  ┌────────────┐  ┌────────────┐            │  │        │
│  │  │  │  Frontend  │  │  Backend   │            │  │        │
│  │  │  │  (Next.js) │  │  (FastAPI) │            │  │        │
│  │  │  │  Port 3000 │  │  Port 8000 │            │  │        │
│  │  │  └─────┬──────┘  └─────┬──────┘            │  │        │
│  │  │        │                │                    │  │        │
│  │  │        │         ┌──────▼──────┐            │  │        │
│  │  │        │         │ ML Service  │            │  │        │
│  │  │        │         │  (FastAPI)  │            │  │        │
│  │  │        │         │  Port 8001  │            │  │        │
│  │  │        │         └──────┬──────┘            │  │        │
│  │  │        │                │                    │  │        │
│  │  │        └────────────────┘                    │  │        │
│  │  └──────────────────────────────────────────────┘  │        │
│  │                                                      │        │
│  │  Security Group: Allow 80, 443, 3000, 8000         │        │
│  └──────────────────┬───────────────────┬─────────────┘        │
│                     │                   │                       │
│           ┌─────────▼────────┐  ┌───────▼────────┐            │
│           │   RDS Postgres   │  │   S3 Buckets   │            │
│           │   (db.t3.micro)  │  │                │            │
│           │                  │  │  - creatives/  │            │
│           │  Multi-tenant DB │  │  - models/     │            │
│           │  with org_id     │  │  - uploads/    │            │
│           └──────────────────┘  └────────────────┘            │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │   CloudWatch     │  │  Secrets Manager │                   │
│  │   Logs & Metrics │  │  (DB credentials,│                   │
│  │                  │  │   JWT secret)    │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                 │
│  ┌──────────────────────────────────────────┐                 │
│  │         IAM Roles & Policies              │                 │
│  │  - EC2 Instance Role (S3, RDS, Secrets)  │                 │
│  │  - User Access Policies                   │                 │
│  └──────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Tenancy Model

**Database-Level Isolation:**
- Every table includes an `organization_id` foreign key
- All queries include `WHERE organization_id = :current_org_id` filter
- Row-Level Security (RLS) policies enforce isolation at the database level
- JWT tokens include `org_id` claim, validated on every request

**Authentication Flow:**
```
1. User logs in → Backend validates credentials
2. Backend generates JWT with claims: {user_id, org_id, role, exp}
3. Frontend stores JWT in httpOnly cookie or localStorage
4. Every API request includes JWT in Authorization header
5. Backend middleware validates JWT and extracts org_id
6. All database queries automatically filter by org_id
```

### Service Communication

- **Frontend → Backend API:** REST over HTTPS, JWT in Authorization header
- **Backend API → ML Service:** Internal HTTP (within Docker network), no auth required (trusted internal network)
- **Backend API → RDS:** PostgreSQL connection with SSL
- **All Services → S3:** AWS SDK with IAM role credentials
- **All Services → Secrets Manager:** AWS SDK for retrieving secrets at startup

## Components and Interfaces

### 1. Frontend (Next.js + Tailwind CSS)

**Technology Stack:**
- Next.js 14 with App Router
- React 18 with TypeScript
- Tailwind CSS for styling
- Recharts for data visualization
- Axios for API calls
- React Query for data fetching and caching

**Key Pages:**
- `/login` - Authentication
- `/dashboard` - Campaign overview with KPIs
- `/campaigns` - Campaign list and detail views
- `/campaigns/upload` - CSV and creative upload
- `/campaigns/[id]` - Individual campaign analysis
- `/creative-studio` - Creative generation and scoring
- `/analytics` - Advanced analytics (attribution, bias audit)
- `/settings` - Organization and user management

**State Management:**
- React Context for auth state (user, org, token)
- React Query for server state (campaigns, predictions)
- Local state for UI interactions

**API Client Interface:**
```typescript
interface ApiClient {
  auth: {
    login(email: string, password: string): Promise<AuthResponse>
    logout(): Promise<void>
    getCurrentUser(): Promise<User>
  }
  campaigns: {
    list(filters?: CampaignFilters): Promise<Campaign[]>
    get(id: string): Promise<Campaign>
    create(data: CampaignCreate): Promise<Campaign>
    uploadCSV(file: File): Promise<UploadResult>
  }
  creatives: {
    upload(campaignId: string, file: File): Promise<Creative>
    score(creativeId: string): Promise<CreativeScore>
    generateVariants(params: GenerationParams): Promise<Creative[]>
  }
  ml: {
    predictEngagement(campaignId: string): Promise<Prediction>
    predictROI(campaignId: string): Promise<ROIPrediction>
    detectBots(campaignId: string): Promise<BotAnalysis>
    analyzeEmotion(text: string): Promise<EmotionScore>
    checkBias(campaignId: string): Promise<BiasReport>
  }
  analytics: {
    getDashboardStats(filters?: DateRange): Promise<DashboardStats>
    getAttribution(campaignIds: string[]): Promise<AttributionResult>
    simulateBudget(scenario: BudgetScenario): Promise<SimulationResult>
  }
}
```

### 2. Backend API (FastAPI)

**Technology Stack:**
- FastAPI 0.104+ with Python 3.11
- SQLAlchemy 2.0 for ORM
- Pydantic v2 for validation
- PyJWT for authentication
- Alembic for database migrations
- Boto3 for AWS SDK
- Asyncio for async operations

**Module Structure:**
```
app/
├── main.py                 # FastAPI app initialization
├── config.py               # Settings (from env vars)
├── database.py             # SQLAlchemy setup
├── models/                 # SQLAlchemy models
│   ├── organization.py
│   ├── user.py
│   ├── campaign.py
│   ├── creative.py
│   ├── prediction.py
│   └── attribution.py
├── schemas/                # Pydantic schemas
│   ├── auth.py
│   ├── campaign.py
│   ├── creative.py
│   └── ml.py
├── routers/                # API route handlers
│   ├── auth.py
│   ├── campaigns.py
│   ├── creatives.py
│   ├── ml.py
│   └── analytics.py
├── services/               # Business logic
│   ├── auth_service.py
│   ├── campaign_service.py
│   ├── ml_client.py        # Calls ML service
│   ├── s3_service.py
│   └── finance_service.py  # ROI, CAC, CLV calculations
├── middleware/
│   ├── auth_middleware.py  # JWT validation
│   └── org_filter.py       # Auto-inject org_id
└── utils/
    ├── security.py         # Password hashing, JWT
    └── validators.py
```

**Key Endpoints:**
```
POST   /auth/register
POST   /auth/login
GET    /auth/me
POST   /auth/invite-user

GET    /campaigns
POST   /campaigns
GET    /campaigns/{id}
POST   /campaigns/upload-csv
DELETE /campaigns/{id}

POST   /creatives/upload
GET    /creatives/{id}
POST   /creatives/{id}/score

POST   /ml/predict-engagement
POST   /ml/predict-roi
POST   /ml/semantic-relevance
POST   /ml/emotion-analysis
POST   /ml/fatigue-prediction
POST   /ml/bot-detection
POST   /ml/generate-creatives
POST   /ml/attribution
POST   /ml/bias-audit

GET    /analytics/dashboard
POST   /analytics/simulate-budget
GET    /analytics/platform-comparison
```

**Authentication Middleware:**
```python
async def verify_jwt(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    request.state.user_id = payload["user_id"]
    request.state.org_id = payload["org_id"]
    request.state.role = payload["role"]
```

### 3. ML Service (FastAPI)

**Technology Stack:**
- FastAPI for serving
- PyTorch 2.1+ for deep learning
- Transformers (HuggingFace) for NLP
- timm for vision models
- CLIP for multimodal
- scikit-learn for traditional ML
- NumPy, Pandas for data processing

**Module Structure:**
```
ml_service/
├── main.py                     # FastAPI app
├── config.py
├── models/                     # Model loading and inference
│   ├── engagement_predictor.py # Multimodal engagement model
│   ├── semantic_analyzer.py    # CLIP-based relevance
│   ├── emotion_classifier.py   # Emotion detection
│   ├── fatigue_predictor.py    # LSTM for ad fatigue
│   ├── bot_detector.py         # GNN for bot detection
│   ├── creative_generator.py   # LLM + diffusion
│   ├── attribution_model.py    # Temporal attribution
│   ├── quality_scorer.py       # Creative quality CNN/ViT
│   └── bias_auditor.py         # Fairness metrics + XAI
├── routers/
│   ├── prediction.py
│   ├── analysis.py
│   └── generation.py
├── services/
│   ├── model_loader.py         # Load models from S3
│   ├── feature_extractor.py    # Text/image embeddings
│   └── inference_cache.py      # Redis cache (optional)
└── utils/
    ├── preprocessing.py
    └── postprocessing.py
```

**Model Registry (S3 Structure):**
```
s3://advision-models/
├── engagement/
│   ├── v1.0.0/
│   │   ├── model.pt
│   │   ├── metadata.json
│   │   └── metrics.json
│   └── v1.1.0/
├── semantic/
│   └── clip-vit-b32/
├── emotion/
│   └── distilbert-emotion/
├── fatigue/
│   └── lstm-v1/
├── bot-detection/
│   └── gnn-v1/
├── creative-gen/
│   └── gpt-3.5-turbo/  # API-based, config only
├── attribution/
│   └── transformer-v1/
├── quality/
│   └── vit-b16/
└── bias/
    └── fairness-v1/
```

## Data Models

### Database Schema (PostgreSQL)

```sql
-- Organizations (Tenants)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'analyst', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_org FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,  -- 'instagram', 'facebook', 'youtube', 'google_ads'
    country VARCHAR(10),
    product_category VARCHAR(100),
    
    -- Spend & Performance Metrics
    spend DECIMAL(12, 2),
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    reach INTEGER,
    revenue DECIMAL(12, 2),
    
    -- Dates
    start_date DATE,
    end_date DATE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'active', 'paused', 'completed'
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_org FOREIGN KEY (organization_id) REFERENCES organizations(id)
);
CREATE INDEX idx_campaigns_org ON campaigns(organization_id);
CREATE INDEX idx_campaigns_platform ON campaigns(platform);
CREATE INDEX idx_campaigns_status ON campaigns(status);

-- Creatives (Ad Assets)
CREATE TABLE creatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Content
    ad_text TEXT,
    image_url VARCHAR(500),  -- S3 URL
    video_url VARCHAR(500),  -- S3 URL (future)
    
    -- Metadata
    creative_type VARCHAR(50),  -- 'image', 'video', 'text', 'carousel'
    format VARCHAR(50),  -- 'square', 'landscape', 'portrait', 'story'
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_org FOREIGN KEY (organization_id) REFERENCES organizations(id),
    CONSTRAINT fk_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
CREATE INDEX idx_creatives_org ON creatives(organization_id);
CREATE INDEX idx_creatives_campaign ON creatives(campaign_id);

-- ML Predictions
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    creative_id UUID REFERENCES creatives(id) ON DELETE SET NULL,
    
    -- Prediction Type
    prediction_type VARCHAR(50) NOT NULL,  -- 'engagement', 'roi', 'quality', 'bot', etc.
    model_version VARCHAR(50) NOT NULL,
    
    -- Prediction Values (JSONB for flexibility)
    predictions JSONB NOT NULL,
    -- Example: {"engagement_rate": 0.045, "confidence": 0.87}
    -- Example: {"roi": 2.3, "cac": 45.2, "clv": 320.5}
    -- Example: {"quality_score": 78, "suggestions": ["increase contrast"]}
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_org FOREIGN KEY (organization_id) REFERENCES organizations(id),
    CONSTRAINT fk_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
    CONSTRAINT fk_creative FOREIGN KEY (creative_id) REFERENCES creatives(id)
);
CREATE INDEX idx_predictions_org ON predictions(organization_id);
CREATE INDEX idx_predictions_campaign ON predictions(campaign_id);
CREATE INDEX idx_predictions_type ON predictions(prediction_type);

-- Attribution Data (Multi-Touch)
CREATE TABLE attribution_touchpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    conversion_id VARCHAR(255) NOT NULL,  -- Groups touchpoints for one conversion
    
    -- Touchpoint Details
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    channel VARCHAR(50) NOT NULL,
    touchpoint_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    position_in_path INTEGER NOT NULL,  -- 1 = first touch, N = last touch
    
    -- Attribution Score (calculated by ML model)
    attribution_score DECIMAL(5, 4),  -- 0.0 to 1.0
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_org FOREIGN KEY (organization_id) REFERENCES organizations(id),
    CONSTRAINT fk_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
CREATE INDEX idx_attribution_org ON attribution_touchpoints(organization_id);
CREATE INDEX idx_attribution_conversion ON attribution_touchpoints(conversion_id);

-- Bot Detection Results
CREATE TABLE bot_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Analysis Results
    bot_probability DECIMAL(5, 4) NOT NULL,  -- 0.0 to 1.0
    red_flags JSONB,  -- ["rapid_actions", "generic_comments", "suspicious_timing"]
    engagement_graph_data JSONB,  -- Graph structure for GNN analysis
    
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_org FOREIGN KEY (organization_id) REFERENCES organizations(id),
    CONSTRAINT fk_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
CREATE INDEX idx_bot_analysis_org ON bot_analysis(organization_id);

-- Bias Audit Results
CREATE TABLE bias_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Fairness Metrics
    demographic_parity DECIMAL(5, 4),
    equalized_odds DECIMAL(5, 4),
    disparate_impact_ratio DECIMAL(5, 4),
    
    -- Detailed Results
    bias_report JSONB,  -- Detailed breakdown by demographic group
    flagged BOOLEAN DEFAULT FALSE,
    
    audited_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_org FOREIGN KEY (organization_id) REFERENCES organizations(id),
    CONSTRAINT fk_campaign FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
CREATE INDEX idx_bias_audits_org ON bias_audits(organization_id);

-- Model Registry (Track deployed models)
CREATE TABLE model_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    s3_path VARCHAR(500) NOT NULL,
    
    -- Metadata
    training_date TIMESTAMP WITH TIME ZONE,
    dataset_size INTEGER,
    evaluation_metrics JSONB,  -- {"mape": 0.12, "r2": 0.85}
    
    -- Deployment
    is_active BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(model_name, version)
);
CREATE INDEX idx_model_registry_active ON model_registry(model_name, is_active);
```

### Key Queries

**1. Get all campaigns for an organization with predictions:**
```sql
SELECT 
    c.*,
    p.predictions->>'engagement_rate' as predicted_engagement,
    p.predictions->>'roi' as predicted_roi
FROM campaigns c
LEFT JOIN predictions p ON c.id = p.campaign_id AND p.prediction_type = 'engagement'
WHERE c.organization_id = :org_id
ORDER BY c.created_at DESC
LIMIT 100;
```

**2. Calculate platform-wise performance:**
```sql
SELECT 
    platform,
    COUNT(*) as campaign_count,
    SUM(spend) as total_spend,
    SUM(clicks)::FLOAT / NULLIF(SUM(impressions), 0) as avg_ctr,
    AVG((p.predictions->>'engagement_rate')::FLOAT) as avg_predicted_engagement
FROM campaigns c
LEFT JOIN predictions p ON c.id = p.campaign_id AND p.prediction_type = 'engagement'
WHERE c.organization_id = :org_id
GROUP BY platform;
```

**3. Get attribution path for a conversion:**
```sql
SELECT 
    conversion_id,
    campaign_id,
    channel,
    touchpoint_timestamp,
    position_in_path,
    attribution_score
FROM attribution_touchpoints
WHERE organization_id = :org_id AND conversion_id = :conversion_id
ORDER BY position_in_path ASC;
```

**4. Find campaigns with high bot probability:**
```sql
SELECT 
    c.id,
    c.name,
    c.platform,
    ba.bot_probability,
    ba.red_flags
FROM campaigns c
INNER JOIN bot_analysis ba ON c.id = ba.campaign_id
WHERE c.organization_id = :org_id AND ba.bot_probability > 0.8
ORDER BY ba.bot_probability DESC;
```

**5. Get active model versions:**
```sql
SELECT model_name, version, s3_path, evaluation_metrics
FROM model_registry
WHERE is_active = TRUE;
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Multi-Tenancy & Security Properties

**Property 1: Organization data isolation**
*For any* two distinct organizations, queries executed with one organization's ID should never return data belonging to the other organization.
**Validates: Requirements 1.1, 1.5**

**Property 2: Role-based access control**
*For any* user and resource, access should be granted if and only if the user belongs to the resource's organization and has sufficient role permissions.
**Validates: Requirements 1.4**

**Property 3: User activation state**
*For any* invitation acceptance, the resulting user account should have is_active=true and the role specified in the invitation.
**Validates: Requirements 1.3**

### Data Ingestion Properties

**Property 4: CSV import completeness**
*For any* valid CSV file, all rows with valid schema should be imported, and the count of imported records should equal the count of valid rows.
**Validates: Requirements 2.1, 2.3**

**Property 5: Partial import resilience**
*For any* CSV file containing both valid and invalid rows, the valid rows should be imported successfully while invalid rows are rejected with error messages, without failing the entire import.
**Validates: Requirements 2.4**

**Property 6: Creative storage uniqueness**
*For any* uploaded creative asset, the system should generate a unique S3 key, and subsequent retrieval using that key should return the same asset.
**Validates: Requirements 2.2**

**Property 7: File format validation**
*For any* uploaded file, acceptance should occur if and only if the format is in {JPEG, PNG, GIF} and size ≤ 10MB.
**Validates: Requirements 2.5**

### Analytics & Dashboard Properties

**Property 8: Dashboard aggregation correctness**
*For any* set of campaigns, the dashboard total spend should equal the sum of individual campaign spends, and average CTR should equal total clicks divided by total impressions.
**Validates: Requirements 3.1**

**Property 9: Filter consistency**
*For any* campaign filter (platform, date range), all metrics and visualizations should reflect only the campaigns matching the filter criteria.
**Validates: Requirements 3.3**

### ML Prediction Properties

**Property 10: Feature extraction completeness**
*For any* campaign with text copy, the NLP model should produce an embedding vector of the expected dimensionality, and for any campaign with images, the vision model should produce an image embedding.
**Validates: Requirements 4.1, 4.2**

**Property 11: ROI calculation correctness**
*For any* campaign with revenue R and spend S, the calculated ROI should equal (R - S) / S, and CAC should equal S / conversions.
**Validates: Requirements 4.4**

### Semantic Relevance Properties

**Property 12: Relevance score range**
*For any* semantic relevance analysis, the output score should be in the range [0, 1], where 0 indicates no relevance and 1 indicates perfect alignment.
**Validates: Requirements 5.1**

**Property 13: Mis-targeting flagging threshold**
*For any* campaign with semantic relevance score < 0.6, the campaign should be flagged as potentially mis-targeted; campaigns with score ≥ 0.6 should not be flagged.
**Validates: Requirements 5.2**

### Emotion Analysis Properties

**Property 14: Emotion classification validity**
*For any* ad copy text, the emotion classifier should return a label from the valid set {positive, negative, neutral, joy, anger, sadness, fear, surprise}.
**Validates: Requirements 6.1**

**Property 15: Sentiment aggregation**
*For any* collection of audience comments, the aggregate sentiment score should be the weighted average of individual comment sentiments, and the dominant emotion should be the most frequent emotion across all comments.
**Validates: Requirements 6.2**

### Ad Fatigue Properties

**Property 16: Fatigue prediction generation**
*For any* campaign with historical interaction data spanning at least 7 days, the fatigue predictor should generate a fatigue risk score in the range [0, 1].
**Validates: Requirements 7.1**

**Property 17: Fatigue-based recommendations**
*For any* campaign with fatigue risk > 0.7, the system should generate a recommendation for creative refresh or rotation; campaigns with risk ≤ 0.7 should not trigger fatigue recommendations.
**Validates: Requirements 7.2**

### Bot Detection Properties

**Property 18: Bot probability range**
*For any* engagement analysis, the bot probability score should be in the range [0, 1], where 0 indicates human behavior and 1 indicates certain bot activity.
**Validates: Requirements 8.1**

**Property 19: Bot flagging threshold**
*For any* account or traffic source with bot probability > 0.8, the system should flag it as likely fake; sources with probability ≤ 0.8 should not be flagged.
**Validates: Requirements 8.2**

**Property 20: Graph cluster detection**
*For any* engagement graph with coordinated inauthentic behavior, the GNN should identify clusters where nodes have suspiciously similar interaction patterns (e.g., same timing, same targets).
**Validates: Requirements 8.3**

### Creative Generation Properties

**Property 21: Variant generation count**
*For any* creative generation request, the system should generate between 3 and 5 text variants, each tailored to the specified persona parameters.
**Validates: Requirements 9.1**

**Property 22: Variant ranking order**
*For any* set of generated variants, they should be returned in descending order of predicted engagement score, such that variant[i].score ≥ variant[i+1].score for all i.
**Validates: Requirements 9.3**

### Attribution Properties

**Property 23: Attribution score normalization**
*For any* conversion path, the sum of attribution scores across all touchpoints should equal 1.0 (within floating-point tolerance of 0.001).
**Validates: Requirements 10.1**

**Property 24: Budget reallocation logic**
*For any* set of channels with attribution scores and ROI values, the recommended budget allocation should prioritize channels with higher (attribution_score × ROI) products.
**Validates: Requirements 10.4**

### Creative Quality Properties

**Property 25: Quality score range**
*For any* creative analysis, the quality score should be in the range [0, 100], and the predicted engagement rate should be in the range [0, 1].
**Validates: Requirements 11.1, 11.2**

**Property 26: Low-quality improvement suggestions**
*For any* creative with quality score < 50, the system should provide at least one specific improvement suggestion; creatives with score ≥ 50 may optionally include suggestions.
**Validates: Requirements 11.4**

### Bias & Fairness Properties

**Property 27: Fairness metric computation**
*For any* campaign with demographic data, the bias auditor should compute demographic parity, equalized odds, and disparate impact ratio for each demographic group.
**Validates: Requirements 12.1, 12.5**

**Property 28: Bias detection and flagging**
*For any* campaign where any fairness metric indicates significant disparity (e.g., disparate impact ratio < 0.8 or > 1.25), the campaign should be flagged and a bias report generated.
**Validates: Requirements 12.2**

### Budget Simulation Properties

**Property 29: Simulation recalculation**
*For any* budget adjustment in the simulator, if spend increases by factor k, then predicted impressions should increase by approximately k (within model uncertainty), and ROI should be recalculated using the new predictions.
**Validates: Requirements 13.1**

**Property 30: Platform reallocation impact**
*For any* budget shift from platform A to platform B, the net ROI change should equal (ROI_B × shifted_amount) - (ROI_A × shifted_amount).
**Validates: Requirements 13.2**

**Property 31: Scenario persistence**
*For any* saved budget scenario, retrieving it should return the exact same budget allocations and predicted outcomes that were saved.
**Validates: Requirements 13.5**

### Model Management Properties

**Property 32: Model versioning**
*For any* trained model stored in S3, the model registry should contain an entry with unique (model_name, version) pair, S3 path, and evaluation metrics.
**Validates: Requirements 14.1**

**Property 33: Active model uniqueness**
*For any* model name, at most one version should have is_active=true at any given time.
**Validates: Requirements 14.2**

### API Properties

**Property 34: Error response structure**
*For any* API error, the response should be a JSON object containing at minimum {error_code: string, message: string}, and the HTTP status code should be in {400, 401, 403, 404, 429, 500, 503}.
**Validates: Requirements 15.2, 15.3**

**Property 35: Request logging completeness**
*For any* API request, the log entry should contain request_id, user_id, org_id, endpoint, method, status_code, and response_time_ms.
**Validates: Requirements 15.5**


## ML System Design

This section maps each of the 8 marketing gaps to specific ML components, model architectures, training approaches, and inference strategies.

### Gap 1: Semantic Mis-targeting

**Problem:** Ads are placed in irrelevant contexts because platforms lack deep content understanding.

**ML Solution:**
- **Model:** CLIP (Contrastive Language-Image Pre-training) ViT-B/32
- **Architecture:** Vision-language model that embeds images and text into a shared semantic space
- **Input Features:**
  - Ad creative (image + text copy)
  - Target context (content description, keywords, or sample content)
- **Output:** Relevance score (0-1) via cosine similarity between ad embedding and context embedding
- **Training:** Use pretrained CLIP; optionally fine-tune on marketing-specific ad-context pairs
- **Inference:** 
  - Encode ad creative: `ad_embedding = clip.encode_image_text(image, text)`
  - Encode context: `context_embedding = clip.encode_text(context_description)`
  - Compute similarity: `relevance = cosine_similarity(ad_embedding, context_embedding)`
- **Evaluation Metrics:** Precision@K for relevant placements, user engagement lift in A/B tests
- **API Endpoint:** `POST /ml/semantic-relevance`

### Gap 2: Emotion-ignorant Ads

**Problem:** Ads don't align with the emotional tone of content or audience sentiment.

**ML Solution:**
- **Model:** DistilBERT-base-uncased fine-tuned on emotion classification (e.g., GoEmotions dataset)
- **Architecture:** Transformer encoder with classification head
- **Input Features:**
  - Ad copy text
  - Audience comments (for aggregate sentiment)
  - Optional: Facial emotion recognition using DeepFace or FER+ on creative images
- **Output:** 
  - Primary emotion: {positive, negative, neutral, joy, anger, sadness, fear, surprise}
  - Confidence scores for each emotion
- **Training:** 
  - Fine-tune DistilBERT on labeled emotion dataset (GoEmotions: 58k Reddit comments with 27 emotions)
  - For facial emotion: Use pretrained FER models (e.g., from DeepFace library)
- **Inference:**
  - Text: `emotion = emotion_classifier(ad_text)`
  - Aggregate: `dominant_emotion = mode([emotion_classifier(comment) for comment in comments])`
  - Face: `face_emotions = deepface.analyze(image, actions=['emotion'])`
- **Evaluation Metrics:** F1 score (target: >0.75), confusion matrix
- **API Endpoint:** `POST /ml/emotion-analysis`

### Gap 3: Primitive Ad Fatigue Detection

**Problem:** Repetitive ad exposure causes declining engagement, but detection is reactive.

**ML Solution:**
- **Model:** LSTM (Long Short-Term Memory) or Transformer for sequence modeling
- **Architecture:** 
  - Input: Sequence of (timestamp, engagement_rate, impressions, creative_id)
  - LSTM with 2 layers, 128 hidden units
  - Output: Fatigue risk score (0-1) and predicted engagement trajectory
- **Input Features:**
  - Time-series of engagement metrics per creative
  - Creative age (days since first shown)
  - Frequency (impressions per day)
  - Engagement trend (slope of engagement over time)
- **Labels:** Binary fatigue indicator (1 if engagement dropped >30% from peak, 0 otherwise)
- **Training:**
  - Collect historical campaign data with engagement time-series
  - Label campaigns where engagement declined significantly
  - Train LSTM to predict fatigue risk given sequence history
- **Inference:**
  - Input last N days of engagement data
  - Output fatigue risk: `risk = lstm_model(engagement_sequence)`
  - If risk > 0.7, recommend creative rotation
- **Evaluation Metrics:** AUC-ROC for fatigue prediction, lead time (days before actual fatigue)
- **API Endpoint:** `POST /ml/fatigue-prediction`

### Gap 4: Fake Influencers & Bot Traffic

**Problem:** Bot-driven engagement inflates metrics and wastes budget.

**ML Solution:**
- **Model:** Graph Neural Network (GNN) + Sequence Model
- **Architecture:**
  - GNN (GraphSAGE or GAT) to model engagement graph (users → content → ads)
  - LSTM to model temporal interaction patterns
  - Combined classifier: bot probability
- **Input Features:**
  - **Graph features:** User-content interaction graph, follower/following ratios, cluster coefficients
  - **Sequence features:** Interaction timestamps, action types (like, comment, share), inter-action intervals
  - **Profile features:** Account age, bio completeness, profile image presence
- **Labels:** Bot (1) vs Human (0) from labeled datasets (e.g., Cresci 2017 bot dataset)
- **Training:**
  - Build engagement graph from interaction logs
  - Extract node embeddings using GNN
  - Train classifier on embeddings + sequence features
- **Inference:**
  - Construct engagement graph for campaign
  - Run GNN to get node embeddings
  - Classify each user: `bot_prob = classifier(gnn_embedding, sequence_features)`
  - Flag users with bot_prob > 0.8
- **Evaluation Metrics:** Precision (target: >0.85), Recall (target: >0.75), F1 score
- **API Endpoint:** `POST /ml/bot-detection`

### Gap 5: Lack of Personalized Creative Generation

**Problem:** A/B testing is manual; creatives are generic and not persona-specific.

**ML Solution:**
- **Model:** 
  - Text: GPT-3.5-turbo or GPT-4 via OpenAI API (or open-source LLaMA-2)
  - Image: Stable Diffusion 2.1 or DALL-E 3 via API
- **Architecture:**
  - LLM with prompt engineering for persona-specific copy
  - Diffusion model for image generation
  - Reinforcement learning (optional): Multi-armed bandit for variant selection
- **Input Features:**
  - Persona parameters: {demographics, interests, tone, platform}
  - Original creative (for variation)
  - Brand guidelines (style, voice)
- **Output:** 3-5 creative variants (text + optional image)
- **Training:**
  - Use pretrained models (GPT, Stable Diffusion)
  - Fine-tune on brand-specific creatives if data available
  - RL: Track variant performance and update selection policy
- **Inference:**
  - Text generation: 
    ```python
    prompt = f"Generate 5 ad copy variants for {persona} promoting {product} in {tone} tone"
    variants = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    ```
  - Image generation:
    ```python
    image = stable_diffusion(prompt=f"{product} ad, {style}, {mood}", num_images=3)
    ```
  - Rank variants by predicted engagement (using creative quality scorer)
- **Evaluation Metrics:** Variant diversity (BLEU distance), engagement lift in A/B tests
- **API Endpoint:** `POST /ml/generate-creatives`

### Gap 6: Weak Multi-Touch Attribution

**Problem:** Hard to determine which touchpoints drove conversions across channels.

**ML Solution:**
- **Model:** Transformer or LSTM for temporal sequence modeling
- **Architecture:**
  - Input: Sequence of touchpoints (channel, timestamp, campaign_id) leading to conversion
  - Transformer encoder with attention mechanism
  - Output: Attribution score for each touchpoint (sums to 1.0)
- **Input Features:**
  - Touchpoint sequence: [(channel_1, time_1, features_1), ..., (channel_n, time_n, features_n)]
  - Time deltas between touchpoints
  - Channel characteristics (cost, typical conversion rate)
- **Labels:** Conversion outcome (1 if converted, 0 otherwise)
- **Training:**
  - Collect conversion paths from tracking data
  - Train model to predict conversion probability given path
  - Use attention weights as attribution scores
- **Inference:**
  - Input conversion path
  - Run Transformer: `attention_weights = transformer(touchpoint_sequence)`
  - Normalize attention weights to get attribution scores
- **Evaluation Metrics:** Conversion prediction AUC, attribution score stability
- **API Endpoint:** `POST /ml/attribution`

### Gap 7: No Predictive Creative Quality Scoring

**Problem:** Creatives are judged after posting, not before launch.

**ML Solution:**
- **Model:** Vision Transformer (ViT-B/16) or EfficientNet-B4
- **Architecture:**
  - Input: Creative image (224x224 or 384x384)
  - ViT encoder → regression head
  - Output: Quality score (0-100) and predicted engagement rate
- **Input Features:**
  - Image pixels
  - Extracted features: color histogram, contrast, text density, face presence
  - Metadata: format, aspect ratio
- **Labels:** Historical engagement rate for each creative
- **Training:**
  - Collect dataset of (creative_image, actual_engagement_rate)
  - Train ViT to predict engagement rate
  - Scale to 0-100 quality score
- **Inference:**
  - Preprocess image: `image_tensor = preprocess(creative_image)`
  - Predict: `quality_score, engagement_pred = vit_model(image_tensor)`
  - If quality_score < 50, generate improvement suggestions using rule-based heuristics (e.g., low contrast → "increase contrast")
- **Evaluation Metrics:** Correlation between predicted and actual engagement (target: >0.7), MAPE
- **API Endpoint:** `POST /ml/score-creative`

### Gap 8: Biased & Non-transparent Targeting

**Problem:** Ad algorithms can unintentionally discriminate; lack of explainability.

**ML Solution:**
- **Model:** Fairness auditing + Explainable AI (SHAP, LIME)
- **Architecture:**
  - Bias detection: Compute fairness metrics (demographic parity, equalized odds, disparate impact)
  - XAI: SHAP (SHapley Additive exPlanations) for feature importance
- **Input Features:**
  - Campaign targeting parameters
  - Demographic data (gender, age, language)
  - Predicted outcomes (engagement, conversion)
- **Output:**
  - Fairness metrics per demographic group
  - Feature importance scores
  - Counterfactual examples ("if feature X changed to Y, prediction would change to Z")
- **Training:** No training required; metrics computed on predictions
- **Inference:**
  - Compute fairness metrics:
    ```python
    demographic_parity = abs(P(Y=1|A=0) - P(Y=1|A=1))
    disparate_impact = P(Y=1|A=0) / P(Y=1|A=1)
    ```
  - Generate SHAP explanations:
    ```python
    explainer = shap.Explainer(model)
    shap_values = explainer(campaign_features)
    ```
  - Flag if disparate_impact < 0.8 or > 1.25
- **Evaluation Metrics:** Fairness metric values, explanation fidelity
- **API Endpoint:** `POST /ml/bias-audit`

### Model Storage & Versioning

**S3 Bucket Structure:**
```
s3://advision-models-{org_id}/
├── engagement/
│   ├── v1.0.0/
│   │   ├── model.pt
│   │   ├── metadata.json  # {training_date, dataset_size, mape: 0.12}
│   │   └── config.json
│   └── v1.1.0/
├── semantic/
│   └── clip-vit-b32/  # Pretrained, no versioning needed
├── emotion/
│   └── distilbert-emotion-v1/
├── fatigue/
│   └── lstm-v1.0.0/
├── bot-detection/
│   └── gnn-v1.0.0/
├── attribution/
│   └── transformer-v1.0.0/
├── quality/
│   └── vit-b16-v1.0.0/
└── bias/
    └── fairness-v1/  # No model, just code
```

**Model Loading at Startup:**
```python
# ml_service/services/model_loader.py
def load_active_models():
    registry = db.query(ModelRegistry).filter(is_active=True).all()
    models = {}
    for entry in registry:
        model_path = download_from_s3(entry.s3_path)
        models[entry.model_name] = torch.load(model_path)
    return models
```

### Inference Optimization

- **Batching:** Group multiple prediction requests to leverage GPU parallelism
- **Caching:** Cache embeddings for frequently accessed creatives (Redis optional)
- **Model Quantization:** Use INT8 quantization for faster inference (PyTorch quantization)
- **Async Processing:** Use FastAPI background tasks for long-running predictions


## Error Handling

### Error Categories

**1. Client Errors (4xx)**
- **400 Bad Request:** Invalid input data (malformed JSON, missing required fields, invalid file format)
- **401 Unauthorized:** Missing or invalid JWT token
- **403 Forbidden:** Valid token but insufficient permissions (e.g., viewer trying to delete campaign)
- **404 Not Found:** Resource doesn't exist or doesn't belong to user's organization
- **409 Conflict:** Resource already exists (e.g., duplicate email on user creation)
- **413 Payload Too Large:** File upload exceeds 10MB limit
- **422 Unprocessable Entity:** Valid syntax but semantic errors (e.g., end_date before start_date)
- **429 Too Many Requests:** Rate limit exceeded

**2. Server Errors (5xx)**
- **500 Internal Server Error:** Unexpected application error
- **502 Bad Gateway:** ML service unavailable
- **503 Service Unavailable:** Database connection failed, S3 unavailable
- **504 Gateway Timeout:** ML inference took too long (>30s)

### Error Response Format

All errors return consistent JSON structure:
```json
{
  "error_code": "INVALID_FILE_FORMAT",
  "message": "Uploaded file must be JPEG, PNG, or GIF",
  "details": {
    "field": "creative_file",
    "received_format": "BMP",
    "allowed_formats": ["JPEG", "PNG", "GIF"]
  },
  "request_id": "req_abc123xyz",
  "timestamp": "2024-12-08T10:30:00Z"
}
```

### Error Handling Strategies

**Backend API:**
```python
# Custom exception classes
class AdVisionException(Exception):
    def __init__(self, error_code: str, message: str, status_code: int, details: dict = None):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}

# Global exception handler
@app.exception_handler(AdVisionException)
async def advision_exception_handler(request: Request, exc: AdVisionException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "request_id": request.state.request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Usage in routes
if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
    raise AdVisionException(
        error_code="INVALID_FILE_FORMAT",
        message="Uploaded file must be JPEG, PNG, or GIF",
        status_code=400,
        details={"received": file.content_type, "allowed": ["image/jpeg", "image/png", "image/gif"]}
    )
```

**ML Service:**
- Wrap model inference in try-except blocks
- Return 502 to backend API if model loading fails
- Return 504 if inference exceeds timeout
- Log all errors with stack traces to CloudWatch

**Frontend:**
- Display user-friendly error messages
- Show technical details in dev mode only
- Implement retry logic for transient errors (503, 504)
- Redirect to login on 401 errors

### Logging Strategy

**Log Levels:**
- **DEBUG:** Detailed diagnostic info (disabled in production)
- **INFO:** General informational messages (API requests, model loading)
- **WARNING:** Unexpected but handled situations (rate limit approaching, slow query)
- **ERROR:** Error conditions that need attention (failed predictions, DB errors)
- **CRITICAL:** System-level failures (cannot connect to DB, S3 unavailable)

**Structured Logging Format:**
```json
{
  "timestamp": "2024-12-08T10:30:00Z",
  "level": "INFO",
  "service": "backend-api",
  "request_id": "req_abc123xyz",
  "user_id": "user_123",
  "org_id": "org_456",
  "endpoint": "/campaigns",
  "method": "POST",
  "status_code": 201,
  "response_time_ms": 145,
  "message": "Campaign created successfully"
}
```

**CloudWatch Integration:**
- Each service (frontend, backend, ml) logs to separate log groups
- Use CloudWatch Insights for querying and analysis
- Set up alarms for error rate thresholds (e.g., >5% error rate)

## Testing Strategy

### Unit Testing

**Backend API (pytest):**
- Test each service function in isolation
- Mock external dependencies (DB, S3, ML service)
- Test cases:
  - Happy path: valid inputs → expected outputs
  - Edge cases: empty lists, boundary values, null fields
  - Error cases: invalid inputs → appropriate exceptions
- Example:
  ```python
  def test_calculate_roi():
      assert calculate_roi(revenue=1000, spend=500) == 1.0
      assert calculate_roi(revenue=500, spend=500) == 0.0
      with pytest.raises(ValueError):
          calculate_roi(revenue=100, spend=0)  # Division by zero
  ```

**ML Service (pytest):**
- Test feature extraction functions
- Test model loading and inference with dummy models
- Test preprocessing and postprocessing logic
- Example:
  ```python
  def test_emotion_classifier():
      text = "I love this product!"
      emotion = emotion_classifier(text)
      assert emotion in ["positive", "joy", "neutral"]
      assert 0 <= emotion_confidence <= 1
  ```

**Frontend (Jest + React Testing Library):**
- Test component rendering
- Test user interactions (button clicks, form submissions)
- Test API client functions with mocked responses
- Example:
  ```javascript
  test('displays campaign list', async () => {
      const campaigns = [{id: 1, name: 'Test Campaign'}];
      mockApiClient.campaigns.list.mockResolvedValue(campaigns);
      render(<CampaignList />);
      expect(await screen.findByText('Test Campaign')).toBeInTheDocument();
  });
  ```

### Property-Based Testing

**Framework:** Hypothesis (Python) for backend and ML service

**Key Properties to Test:**
- **Idempotence:** Calling the same endpoint twice with same data produces same result
- **Invariants:** Organization data isolation, attribution scores sum to 1.0
- **Round-trip:** Serialize/deserialize preserves data
- **Monotonicity:** Increasing spend increases predicted impressions
- **Commutativity:** Order of operations doesn't matter (e.g., filtering then aggregating vs aggregating then filtering)

**Example:**
```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=1e6), st.floats(min_value=0, max_value=1e6))
def test_roi_calculation_property(revenue, spend):
    if spend > 0:
        roi = calculate_roi(revenue, spend)
        # Property: ROI should be positive if revenue > spend
        if revenue > spend:
            assert roi > 0
        # Property: ROI should be negative if revenue < spend
        elif revenue < spend:
            assert roi < 0
        # Property: ROI should be zero if revenue == spend
        else:
            assert abs(roi) < 0.001  # Floating point tolerance
```

**Property Tests for ML Models:**
- **Semantic relevance:** Identical ad and context should have relevance = 1.0
- **Emotion consistency:** Same text should always produce same emotion label
- **Bot detection:** Known human patterns should have bot_prob < 0.5
- **Attribution normalization:** Sum of attribution scores should always equal 1.0

### Integration Testing

**API Integration Tests:**
- Test full request-response cycle with real DB (test database)
- Test authentication flow: register → login → access protected endpoint
- Test multi-tenancy: create two orgs, verify data isolation
- Test file upload: upload creative → verify S3 storage → retrieve URL

**ML Pipeline Integration:**
- Test end-to-end prediction flow: upload campaign → extract features → predict engagement → store result
- Test model versioning: deploy new model → verify active model updated → rollback → verify old model active

**Database Integration:**
- Test complex queries with real data
- Test transaction rollback on errors
- Test foreign key constraints and cascading deletes

### End-to-End Testing

**Framework:** Playwright or Cypress for frontend E2E tests

**Test Scenarios:**
- User registration and login
- Upload campaign CSV and creatives
- View dashboard with predictions
- Generate creative variants
- Run budget simulation
- View bias audit report

**Example E2E Test:**
```javascript
test('complete campaign creation flow', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await page.goto('/campaigns/upload');
    await page.setInputFiles('input[type="file"]', 'test-campaigns.csv');
    await page.click('button:has-text("Upload")');
    
    await expect(page.locator('text=Upload successful')).toBeVisible();
    await page.goto('/dashboard');
    await expect(page.locator('text=Total Campaigns')).toBeVisible();
});
```

### Performance Testing

**Load Testing (Locust or k6):**
- Simulate 100 concurrent users
- Test API response times under load
- Test ML inference throughput (predictions per second)
- Identify bottlenecks (DB queries, model inference)

**Benchmarks:**
- Single prediction: < 3 seconds
- Batch prediction (100 campaigns): < 30 seconds
- Dashboard load: < 2 seconds
- CSV upload (1000 rows): < 10 seconds

### Test Coverage Goals

- **Backend API:** >80% code coverage
- **ML Service:** >70% code coverage (excluding model training code)
- **Frontend:** >70% component coverage
- **Property tests:** All critical business logic properties covered
- **Integration tests:** All major user flows covered

### Continuous Testing

**CI/CD Pipeline (GitHub Actions):**
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/unit --cov
      - name: Run property tests
        run: pytest tests/property --hypothesis-profile=ci
      - name: Run integration tests
        run: pytest tests/integration
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Test Environments:**
- **Local:** Docker Compose with test DB and mock ML models
- **CI:** GitHub Actions with PostgreSQL service container
- **Staging:** AWS environment with real services but test data
- **Production:** Smoke tests only (health checks, basic API calls)


## AWS Deployment Architecture

### Deployment Strategy: EC2 with Docker Compose (Learner Lab Compatible)

Given AWS Learner Lab constraints (limited services, no persistent resources between sessions), we'll use a single EC2 instance with Docker Compose for development and testing. This approach is cost-effective and provides a clear migration path to ECS Fargate for production.

### AWS Resources

**1. VPC & Networking**
- **VPC:** Use default VPC or create custom VPC with CIDR 10.0.0.0/16
- **Subnets:**
  - Public subnet (10.0.1.0/24) for EC2 instance
  - Private subnet (10.0.2.0/24) for RDS (optional, can use public for dev)
- **Internet Gateway:** Attached to VPC for public internet access
- **Security Groups:**
  - **EC2 Security Group:**
    - Inbound: 22 (SSH), 80 (HTTP), 443 (HTTPS), 3000 (Next.js dev), 8000 (FastAPI)
    - Outbound: All traffic
  - **RDS Security Group:**
    - Inbound: 5432 (PostgreSQL) from EC2 security group only
    - Outbound: None needed

**2. EC2 Instance**
- **Instance Type:** t3.medium (2 vCPU, 4 GB RAM) - sufficient for MVP
  - Alternative: t3.large (2 vCPU, 8 GB RAM) if ML inference is slow
- **AMI:** Amazon Linux 2023 or Ubuntu 22.04 LTS
- **Storage:** 30 GB gp3 EBS volume (20 GB for OS + Docker images, 10 GB for logs)
- **IAM Role:** EC2InstanceRole with policies for S3, RDS, Secrets Manager, CloudWatch
- **Key Pair:** Create and download for SSH access
- **Elastic IP:** Attach for persistent public IP (optional, costs $0 if attached)

**3. RDS PostgreSQL**
- **Instance Class:** db.t3.micro (1 vCPU, 1 GB RAM) - free tier eligible
- **Engine:** PostgreSQL 15.x
- **Storage:** 20 GB gp3 (free tier: 20 GB)
- **Multi-AZ:** Disabled for dev (enable for production)
- **Backup:** 7-day retention
- **Encryption:** Enabled at rest (AES-256)
- **Public Access:** No (access via EC2 only)
- **Parameter Group:** Default with SSL enforcement

**4. S3 Buckets**
- **advision-creatives-{org_id}:** Store uploaded images/videos
  - Versioning: Enabled
  - Encryption: SSE-S3 (AES-256)
  - Lifecycle: Move to Glacier after 90 days (optional)
- **advision-models:** Store ML model artifacts
  - Versioning: Enabled
  - Encryption: SSE-S3
- **advision-uploads:** Temporary storage for CSV uploads
  - Lifecycle: Delete after 7 days
- **Bucket Policies:** Restrict access to EC2 instance role only

**5. Secrets Manager**
- **advision/db-credentials:** RDS username and password
- **advision/jwt-secret:** JWT signing key
- **advision/openai-api-key:** OpenAI API key (for creative generation)
- **Rotation:** Enable automatic rotation for DB credentials (30 days)

**6. CloudWatch**
- **Log Groups:**
  - `/advision/frontend`
  - `/advision/backend`
  - `/advision/ml-service`
- **Metrics:**
  - EC2: CPU, memory, disk, network
  - RDS: Connections, CPU, storage
  - Custom: API request count, error rate, prediction latency
- **Alarms:**
  - EC2 CPU > 80% for 5 minutes
  - RDS connections > 80% of max
  - API error rate > 5%

**7. IAM Roles & Policies**

**EC2 Instance Role (AdVisionEC2Role):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::advision-*/*",
        "arn:aws:s3:::advision-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:advision/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/advision/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

### Docker Compose Setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - S3_BUCKET_CREATIVES=${S3_BUCKET_CREATIVES}
      - S3_BUCKET_MODELS=${S3_BUCKET_MODELS}
      - ML_SERVICE_URL=http://ml-service:8001
      - AWS_REGION=${AWS_REGION}
    depends_on:
      - ml-service
    restart: unless-stopped

  ml-service:
    build:
      context: ./ml-service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - S3_BUCKET_MODELS=${S3_BUCKET_MODELS}
      - AWS_REGION=${AWS_REGION}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - model-cache:/app/models  # Cache downloaded models
    restart: unless-stopped

volumes:
  model-cache:
```

### Deployment Steps

**Phase 1: AWS Resource Setup**

1. **Create VPC and Subnets** (if not using default)
   ```bash
   aws ec2 create-vpc --cidr-block 10.0.0.0/16
   aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
   ```

2. **Create Security Groups**
   ```bash
   aws ec2 create-security-group --group-name advision-ec2-sg --description "AdVision EC2 Security Group"
   aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 22 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 80 --cidr 0.0.0.0/0
   aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 443 --cidr 0.0.0.0/0
   ```

3. **Create RDS Instance**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier advision-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password <strong-password> \
     --allocated-storage 20 \
     --vpc-security-group-ids sg-xxx \
     --backup-retention-period 7 \
     --storage-encrypted
   ```

4. **Create S3 Buckets**
   ```bash
   aws s3 mb s3://advision-creatives-prod
   aws s3 mb s3://advision-models
   aws s3 mb s3://advision-uploads
   ```

5. **Store Secrets in Secrets Manager**
   ```bash
   aws secretsmanager create-secret \
     --name advision/db-credentials \
     --secret-string '{"username":"admin","password":"<password>","host":"<rds-endpoint>","port":"5432","database":"advision"}'
   
   aws secretsmanager create-secret \
     --name advision/jwt-secret \
     --secret-string '<random-256-bit-key>'
   ```

6. **Create IAM Role for EC2**
   ```bash
   aws iam create-role --role-name AdVisionEC2Role --assume-role-policy-document file://trust-policy.json
   aws iam put-role-policy --role-name AdVisionEC2Role --policy-name AdVisionEC2Policy --policy-document file://ec2-policy.json
   aws iam create-instance-profile --instance-profile-name AdVisionEC2Profile
   aws iam add-role-to-instance-profile --instance-profile-name AdVisionEC2Profile --role-name AdVisionEC2Role
   ```

**Phase 2: EC2 Instance Setup**

7. **Launch EC2 Instance**
   ```bash
   aws ec2 run-instances \
     --image-id ami-xxx \
     --instance-type t3.medium \
     --key-name advision-key \
     --security-group-ids sg-xxx \
     --iam-instance-profile Name=AdVisionEC2Profile \
     --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":30,"VolumeType":"gp3"}}]' \
     --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=AdVision-Server}]'
   ```

8. **SSH into EC2 and Install Docker**
   ```bash
   ssh -i advision-key.pem ec2-user@<ec2-public-ip>
   
   # Install Docker
   sudo yum update -y
   sudo yum install docker -y
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ec2-user
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

9. **Clone Repository and Configure Environment**
   ```bash
   git clone https://github.com/your-org/advision-ai.git
   cd advision-ai
   
   # Fetch secrets from Secrets Manager
   aws secretsmanager get-secret-value --secret-id advision/db-credentials --query SecretString --output text > .env.secrets
   
   # Create .env file
   cat > .env << EOF
   DATABASE_URL=postgresql://admin:<password>@<rds-endpoint>:5432/advision
   JWT_SECRET=<jwt-secret>
   S3_BUCKET_CREATIVES=advision-creatives-prod
   S3_BUCKET_MODELS=advision-models
   AWS_REGION=us-east-1
   OPENAI_API_KEY=<openai-key>
   EOF
   ```

10. **Build and Run Docker Containers**
    ```bash
    docker-compose build
    docker-compose up -d
    
    # Check logs
    docker-compose logs -f
    ```

11. **Run Database Migrations**
    ```bash
    docker-compose exec backend alembic upgrade head
    ```

**Phase 3: Model Deployment**

12. **Upload Pretrained Models to S3**
    ```bash
    # Download models locally first
    python scripts/download_models.py  # Downloads CLIP, DistilBERT, etc.
    
    # Upload to S3
    aws s3 sync ./models/ s3://advision-models/
    ```

13. **Verify ML Service**
    ```bash
    curl http://localhost:8001/health
    # Should return: {"status": "ok", "models_loaded": ["engagement", "semantic", "emotion"]}
    ```

**Phase 4: Testing & Verification**

14. **Test API Endpoints**
    ```bash
    # Health check
    curl http://<ec2-public-ip>:8000/health
    
    # Register user
    curl -X POST http://<ec2-public-ip>:8000/auth/register \
      -H "Content-Type: application/json" \
      -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'
    
    # Login
    curl -X POST http://<ec2-public-ip>:8000/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"test@example.com","password":"password123"}'
    ```

15. **Test Frontend**
    - Navigate to `http://<ec2-public-ip>:3000`
    - Register and login
    - Upload test campaign CSV
    - Verify dashboard displays data

**Phase 5: Production Hardening (Optional)**

16. **Set up HTTPS with Let's Encrypt**
    ```bash
    sudo yum install certbot python3-certbot-nginx -y
    sudo certbot --nginx -d advision.yourdomain.com
    ```

17. **Configure Nginx Reverse Proxy**
    ```nginx
    server {
        listen 80;
        server_name advision.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl;
        server_name advision.yourdomain.com;
        
        ssl_certificate /etc/letsencrypt/live/advision.yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/advision.yourdomain.com/privkey.pem;
        
        location / {
            proxy_pass http://localhost:3000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```

18. **Set up CloudWatch Logs**
    ```bash
    # Install CloudWatch agent
    sudo yum install amazon-cloudwatch-agent -y
    
    # Configure log collection
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
      -a fetch-config \
      -m ec2 \
      -s \
      -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
    ```

### Cost Estimation (Monthly)

**AWS Free Tier (First 12 Months):**
- EC2 t3.micro: 750 hours/month (free)
- RDS db.t3.micro: 750 hours/month (free)
- S3: 5 GB storage (free)
- Data transfer: 15 GB out (free)

**Beyond Free Tier (Minimal Usage):**
- EC2 t3.medium: ~$30/month (730 hours × $0.0416/hour)
- RDS db.t3.micro: ~$15/month (730 hours × $0.017/hour)
- S3 storage: ~$1/month (20 GB × $0.023/GB)
- Data transfer: ~$5/month (50 GB × $0.09/GB)
- CloudWatch: ~$3/month (logs + metrics)
- **Total: ~$54/month**

**Cost Optimization Tips:**
- Use t3.micro for EC2 during development (~$7/month)
- Stop EC2 instance when not in use (Learner Lab resets anyway)
- Use S3 Intelligent-Tiering for automatic cost optimization
- Delete old logs and unused model versions
- Use spot instances for ML training (not inference)

### Migration Path to ECS Fargate (Production)

When ready to scale beyond single EC2:

1. **Push Docker images to ECR**
   ```bash
   aws ecr create-repository --repository-name advision-frontend
   docker tag advision-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/advision-frontend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/advision-frontend:latest
   ```

2. **Create ECS Cluster and Task Definitions**
   - Define tasks for frontend, backend, ml-service
   - Use Fargate launch type (serverless)
   - Configure auto-scaling based on CPU/memory

3. **Set up Application Load Balancer**
   - Route `/api/*` to backend service
   - Route `/*` to frontend service
   - Enable HTTPS with ACM certificate

4. **Benefits of ECS Fargate:**
   - Auto-scaling based on load
   - No server management
   - Better fault tolerance (multi-AZ)
   - Easier CI/CD integration

