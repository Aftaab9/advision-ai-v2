# Implementation Plan

- [ ] 1. Set up project structure and development environment
  - Create monorepo structure with frontend/, backend/, ml-service/ directories
  - Set up Docker and docker-compose.yml for local development
  - Configure environment variables and .env.example files
  - Initialize Git repository with .gitignore
  - _Requirements: All_

- [ ] 2. Implement database schema and migrations
  - [ ] 2.1 Set up SQLAlchemy with PostgreSQL connection
    - Configure database.py with connection pooling and session management
    - _Requirements: 1.1, 1.5_
  
  - [ ] 2.2 Create organization and user models
    - Implement Organization model with id, name, slug, timestamps
    - Implement User model with org_id, email, password_hash, role, is_active
    - Add indexes on organization_id and email fields
    - _Requirements: 1.1, 1.3, 1.4_
  
  - [ ] 2.3 Write property test for organization data isolation
    - **Property 1: Organization data isolation**
    - **Validates: Requirements 1.1, 1.5**
  
  - [ ] 2.4 Create campaign and creative models
    - Implement Campaign model with all metrics fields (spend, impressions, clicks, etc.)
    - Implement Creative model with ad_text, image_url, creative_type
    - Add foreign keys and indexes
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 2.5 Create ML-related models
    - Implement Prediction model with JSONB predictions field
    - Implement AttributionTouchpoint model for multi-touch attribution
    - Implement BotAnalysis and BiasAudit models
    - Implement ModelRegistry for model versioning
    - _Requirements: 4.1, 8.1, 10.1, 12.1, 14.1_
  
  - [ ] 2.6 Set up Alembic for database migrations
    - Initialize Alembic configuration
    - Create initial migration with all tables
    - Test migration up and down
    - _Requirements: All database requirements_

- [ ] 3. Implement authentication and authorization
  - [ ] 3.1 Create authentication service
    - Implement password hashing with bcrypt
    - Implement JWT token generation and validation
    - Create login and registration endpoints
    - _Requirements: 1.2, 1.3_
  
  - [ ] 3.2 Implement JWT middleware
    - Create middleware to extract and validate JWT from Authorization header
    - Inject user_id, org_id, role into request state
    - Handle token expiration and invalid tokens
    - _Requirements: 1.4_
  
  - [ ] 3.3 Write property test for role-based access control
    - **Property 2: Role-based access control**
    - **Validates: Requirements 1.4**
  
  - [ ] 3.4 Implement organization filtering middleware
    - Create middleware to automatically inject org_id filter in all queries
    - Ensure all database queries respect multi-tenancy
    - _Requirements: 1.5_
  
  - [ ] 3.5 Write property test for user activation
    - **Property 3: User activation state**
    - **Validates: Requirements 1.3**

- [ ] 4. Implement campaign management API
  - [ ] 4.1 Create campaign CRUD endpoints
    - POST /campaigns - create campaign
    - GET /campaigns - list campaigns with filtering
    - GET /campaigns/{id} - get campaign details
    - DELETE /campaigns/{id} - delete campaign
    - _Requirements: 2.1, 2.3_
  
  - [ ] 4.2 Implement CSV upload and parsing
    - Create POST /campaigns/upload-csv endpoint
    - Parse CSV with pandas, validate schema
    - Handle partial imports (valid rows succeed, invalid rows return errors)
    - _Requirements: 2.1, 2.4_
  
  - [ ] 4.3 Write property test for CSV import completeness
    - **Property 4: CSV import completeness**
    - **Validates: Requirements 2.1, 2.3**
  
  - [ ] 4.4 Write property test for partial import resilience
    - **Property 5: Partial import resilience**
    - **Validates: Requirements 2.4**
  
  - [ ] 4.5 Implement creative upload to S3
    - Create POST /creatives/upload endpoint
    - Validate file format (JPEG, PNG, GIF) and size (<10MB)
    - Generate unique S3 key and upload to S3
    - Store creative metadata in database
    - _Requirements: 2.2, 2.5_
  
  - [ ] 4.6 Write property testt for creative storage uniqueness
    - **Property 6: Creative storage uniqueness**
    - **Validates: Requirements 2.2**
  
  - [ ] 4.7 Write property test for file format validation
    - **Property 7: File format validation**
    - **Validates: Requirements 2.5**

- [ ] 5. Implement dashboard and analytics API
  - [ ] 5.1 Create dashboard summary endpoint
    - Implement GET /analytics/dashboard
    - Calculate total campaigns, total spend, average CTR
    - Calculate platform-wise engagement rates
    - _Requirements: 3.1_
  
  - [ ] 5.2 Write property test for dashboard aggregation correctness
    - **Property 8: Dashboard aggregation correctness**
    - **Validates: Requirements 3.1**
  
  - [ ] 5.3 Implement campaign filtering
    - Add query parameters for platform, date range, status
    - Apply filters to all dashboard metrics
    - _Requirements: 3.3_
  
  - [ ] 5.4 Write property test for filter consistency
    - **Property 9: Filter consistency**
    - **Validates: Requirements 3.3**
  
  - [ ] 5.5 Implement finance metrics calculation
    - Create service functions for ROI, CAC, CLV, payback period
    - Add GET /campaigns/{id}/finance endpoint
    - _Requirements: 4.4_
  
  - [ ] 5.6 Write property test for ROI calculation correctness
    - **Property 11: ROI calculation correctness**
    - **Validates: Requirements 4.4**

- [ ] 6. Set up ML service infrastructure
  - [ ] 6.1 Create ML service FastAPI application
    - Initialize FastAPI app with health check endpoint
    - Set up model loading from S3 at startup
    - Configure logging and error handling
    - _Requirements: 4.1, 4.2_
  
  - [ ] 6.2 Implement model loader service
    - Create function to download models from S3
    - Load models into memory with caching
    - Query ModelRegistry for active model versions
    - _Requirements: 14.1, 14.2_
  
  - [ ] 6.3 Write property test for model versioning
    - **Property 32: Model versioning**
    - **Validates: Requirements 14.1**
  
  - [ ] 6.4 Write property test for active model uniqueness
    - **Property 33: Active model uniqueness**
    - **Validates: Requirements 14.2**
  
  - [ ] 6.5 Create feature extraction utilities
    - Implement text embedding extraction using transformers
    - Implement image embedding extraction using vision models
    - _Requirements: 4.1, 4.2_
  
  - [ ] 6.6 Write property test for feature extraction completeness
    - **Property 10: Feature extraction completeness**
    - **Validates: Requirements 4.1, 4.2**

- [ ] 7. Implement semantic relevance analysis (Gap 1)
  - [ ] 7.1 Load CLIP model for multimodal embeddings
    - Download and cache CLIP ViT-B/32 from HuggingFace
    - Create inference function for image+text encoding
    - _Requirements: 5.1, 5.3_
  
  - [ ] 7.2 Implement semantic relevance scoring
    - Create POST /ml/semantic-relevance endpoint
    - Encode ad creative and target context
    - Compute cosine similarity as relevance score
    - _Requirements: 5.1, 5.4_
  
  - [ ] 7.3 Write property test for relevance score range
    - **Property 12: Relevance score range**
    - **Validates: Requirements 5.1**
  
  - [ ] 7.4 Implement mis-targeting flagging logic
    - Flag campaigns with relevance score < 0.6
    - Generate explanation text for flagged campaigns
    - _Requirements: 5.2_
  
  - [ ] 7.5 Write property test for mis-targeting flagging threshold
    - **Property 13: Mis-targeting flagging threshold**
    - **Validates: Requirements 5.2**

- [ ] 8. Implement emotion analysis (Gap 2)
  - [ ] 8.1 Load emotion classification model
    - Download DistilBERT fine-tuned on GoEmotions dataset
    - Create inference function for emotion classification
    - _Requirements: 6.1, 6.4_
  
  - [ ] 8.2 Implement emotion analysis endpoint
    - Create POST /ml/emotion-analysis endpoint
    - Classify ad copy into emotion categories
    - Return emotion label and confidence scores
    - _Requirements: 6.1_
  
  - [ ] 8.3 Write property test for emotion classification validity
    - **Property 14: Emotion classification validity**
    - **Validates: Requirements 6.1**
  
  - [ ] 8.4 Implement sentiment aggregation for comments
    - Accept array of comments as input
    - Compute aggregate sentiment scores
    - Identify dominant emotion across comments
    - _Requirements: 6.2_
  
  - [ ] 8.5 Write property test for sentiment aggregation
    - **Property 15: Sentiment aggregation**
    - **Validates: Requirements 6.2**
  
  - [ ] 8.6 Add facial emotion recognition (optional)
    - Integrate DeepFace library for face detection and emotion
    - Analyze faces in creative images
    - Return emotion distribution scores
    - _Requirements: 6.5_

- [ ] 9. Implement ad fatigue prediction (Gap 3)
  - [ ] 9.1 Create LSTM model for fatigue prediction
    - Define LSTM architecture (2 layers, 128 hidden units)
    - Implement training script with synthetic time-series data
    - Save trained model to S3
    - _Requirements: 7.1, 7.3_
  
  - [ ] 9.2 Implement fatigue prediction endpoint
    - Create POST /ml/fatigue-prediction endpoint
    - Accept historical engagement time-series as input
    - Return fatigue risk score (0-1)
    - _Requirements: 7.1_
  
  - [ ] 9.3 Write property test for fatigue prediction generation
    - **Property 16: Fatigue prediction generation**
    - **Validates: Requirements 7.1**
  
  - [ ] 9.4 Implement fatigue-based recommendations
    - Generate creative refresh recommendations when risk > 0.7
    - Specify which creatives to pause and when to rotate
    - _Requirements: 7.2, 7.4_
  
  - [ ] 9.5 Write property test for fatigue-based recommendations
    - **Property 17: Fatigue-based recommendations**
    - **Validates: Requirements 7.2**

- [ ] 10. Implement bot detection (Gap 4)
  - [ ] 10.1 Create GNN model for engagement graph analysis
    - Define GraphSAGE or GAT architecture
    - Implement training script with labeled bot dataset
    - Save trained model to S3
    - _Requirements: 8.1, 8.3_
  
  - [ ] 10.2 Implement bot detection endpoint
    - Create POST /ml/bot-detection endpoint
    - Build engagement graph from interaction data
    - Run GNN inference to get bot probabilities
    - _Requirements: 8.1_
  
  - [ ] 10.3 Write property test for bot probability range
    - **Property 18: Bot probability range**
    - **Validates: Requirements 8.1**
  
  - [ ] 10.4 Implement bot flagging and reporting
    - Flag accounts with bot_prob > 0.8
    - Generate red flags list (rapid actions, generic comments, etc.)
    - Store results in bot_analysis table
    - _Requirements: 8.2, 8.4_
  
  - [ ] 10.5 Write property test for bot flagging threshold
    - **Property 19: Bot flagging threshold**
    - **Validates: Requirements 8.2**
  
  - [ ] 10.6 Write property test for graph cluster detection
    - **Property 20: Graph cluster detection**
    - **Validates: Requirements 8.3**

- [ ] 11. Implement creative generation (Gap 5)
  - [ ] 11.1 Set up OpenAI API integration
    - Configure OpenAI API client with API key
    - Implement retry logic and error handling
    - _Requirements: 9.1_
  
  - [ ] 11.2 Implement text variant generation
    - Create POST /ml/generate-creatives endpoint
    - Generate 3-5 text variants using GPT-3.5-turbo
    - Tailor variants to persona parameters (demographics, tone, platform)
    - _Requirements: 9.1, 9.4_
  
  - [ ] 11.3 Write property test for variant generation count
    - **Property 21: Variant generation count**
    - **Validates: Requirements 9.1**
  
  - [ ] 11.4 Implement variant ranking by predicted engagement
    - Score each variant using creative quality model
    - Sort variants by predicted engagement score
    - _Requirements: 9.3_
  
  - [ ] 11.5 Write property test for variant ranking order
    - **Property 22: Variant ranking order**
    - **Validates: Requirements 9.3**
  
  - [ ] 11.6 Add image generation with Stable Diffusion (optional)
    - Integrate Stable Diffusion API or local model
    - Generate visual variants from text prompts
    - _Requirements: 9.2_

- [ ] 12. Implement multi-touch attribution (Gap 6)
  - [ ] 12.1 Create Transformer model for attribution
    - Define Transformer architecture with attention mechanism
    - Implement training script with conversion path data
    - Save trained model to S3
    - _Requirements: 10.1, 10.3_
  
  - [ ] 12.2 Implement attribution analysis endpoint
    - Create POST /ml/attribution endpoint
    - Accept conversion path (sequence of touchpoints)
    - Return attribution scores for each touchpoint
    - _Requirements: 10.1, 10.2_
  
  - [ ] 12.3 Write property test for attribution score normalization
    - **Property 23: Attribution score normalization**
    - **Validates: Requirements 10.1**
  
  - [ ] 12.4 Implement budget reallocation recommendations
    - Calculate (attribution_score × ROI) for each channel
    - Recommend budget shifts to higher-performing channels
    - _Requirements: 10.4_
  
  - [ ] 12.5 Write property test for budget reallocation logic
    - **Property 24: Budget reallocation logic**
    - **Validates: Requirements 10.4**

- [ ] 13. Implement creative quality scoring (Gap 7)
  - [ ] 13.1 Create Vision Transformer model for quality scoring
    - Load pretrained ViT-B/16 from timm or HuggingFace
    - Fine-tune on creative performance dataset (if available)
    - Save trained model to S3
    - _Requirements: 11.1, 11.3_
  
  - [ ] 13.2 Implement creative quality scoring endpoint
    - Create POST /ml/score-creative endpoint
    - Analyze visual composition, color, text placement
    - Return quality score (0-100) and predicted engagement
    - _Requirements: 11.1, 11.2_
  
  - [ ] 13.3 Write property test for quality score range
    - **Property 25: Quality score range**
    - **Validates: Requirements 11.1, 11.2**
  
  - [ ] 13.4 Implement improvement suggestions
    - Generate suggestions for creatives with score < 50
    - Use rule-based heuristics (contrast, text density, etc.)
    - _Requirements: 11.4_
  
  - [ ] 13.5 Write property test for low-quality improvement suggestions
    - **Property 26: Low-quality improvement suggestions**
    - **Validates: Requirements 11.4**

- [ ] 14. Implement bias auditing and explainability (Gap 8)
  - [ ] 14.1 Implement fairness metrics calculation
    - Create functions for demographic parity, equalized odds, disparate impact
    - Accept campaign data with demographic breakdowns
    - _Requirements: 12.1, 12.5_
  
  - [ ] 14.2 Write property test for fairness metric computation
    - **Property 27: Fairness metric computation**
    - **Validates: Requirements 12.1, 12.5**
  
  - [ ] 14.3 Implement bias detection and flagging
    - Create POST /ml/bias-audit endpoint
    - Flag campaigns with disparate impact < 0.8 or > 1.25
    - Generate bias report with specific disparities
    - _Requirements: 12.2_
  
  - [ ] 14.4 Write property test for bias detection and flagging
    - **Property 28: Bias detection and flagging**
    - **Validates: Requirements 12.2**
  
  - [ ] 14.5 Implement SHAP explainability
    - Integrate SHAP library for feature importance
    - Generate explanations for targeting decisions
    - Provide counterfactual examples
    - _Requirements: 12.3, 12.4_

- [ ] 15. Implement budget simulation
  - [ ] 15.1 Create budget simulation endpoint
    - Implement POST /analytics/simulate-budget
    - Accept budget adjustments as input
    - Recalculate predicted impressions, clicks, conversions, ROI
    - _Requirements: 13.1_
  
  - [ ] 15.2 Write property test for simulation recalculation
    - **Property 29: Simulation recalculation**
    - **Validates: Requirements 13.1**
  
  - [ ] 15.3 Implement platform reallocation impact
    - Calculate net ROI change when shifting budget between platforms
    - Recommend optimal allocation
    - _Requirements: 13.2_
  
  - [ ] 15.4 Write property test for platform reallocation impact
    - **Property 30: Platform reallocation impact**
    - **Validates: Requirements 13.2**
  
  - [ ] 15.5 Implement scenario saving and retrieval
    - Store budget scenarios in database
    - Implement GET /analytics/scenarios and POST /analytics/scenarios
    - _Requirements: 13.5_
  
  - [ ] 15.6 Write property test for scenario persistence
    - **Property 31: Scenario persistence**
    - **Validates: Requirements 13.5**

- [ ] 16. Implement error handling and API standards
  - [ ] 16.1 Create custom exception classes
    - Define AdVisionException with error_code, message, status_code
    - Create specific exceptions (InvalidFileFormat, Unauthorized, etc.)
    - _Requirements: 15.2_
  
  - [ ] 16.2 Implement global exception handler
    - Create FastAPI exception handler for consistent error responses
    - Include request_id, timestamp in all error responses
    - _Requirements: 15.2, 15.3_
  
  - [ ] 16.3 Write property test for error response structure
    - **Property 34: Error response structure**
    - **Validates: Requirements 15.2, 15.3**
  
  - [ ] 16.4 Implement request logging middleware
    - Log all API requests with request_id, user_id, org_id, endpoint, status_code, response_time
    - Send logs to CloudWatch
    - _Requirements: 15.5_
  
  - [ ] 16.5 Write property test for request logging completeness
    - **Property 35: Request logging completeness**
    - **Validates: Requirements 15.5**
  
  - [ ] 16.6 Generate OpenAPI documentation
    - Configure FastAPI to auto-generate OpenAPI spec
    - Add descriptions and examples to all endpoints
    - _Requirements: 15.1_

- [ ] 17. Build frontend application
  - [ ] 17.1 Set up Next.js project with TypeScript
    - Initialize Next.js 14 with App Router
    - Configure Tailwind CSS
    - Set up API client with Axios
    - _Requirements: All frontend requirements_
  
  - [ ] 17.2 Implement authentication pages
    - Create /login page with email/password form
    - Create /register page for new users
    - Implement JWT storage and auth context
    - _Requirements: 1.2, 1.3_
  
  - [ ] 17.3 Create dashboard page
    - Display total campaigns, total spend, average CTR
    - Show platform-wise engagement rates
    - Add filters for platform and date range
    - Implement charts with Recharts (time-series, bar charts)
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  
  - [ ] 17.4 Create campaign management pages
    - Implement /campaigns page with campaign list
    - Create /campaigns/upload page for CSV and creative upload
    - Implement /campaigns/[id] page for campaign details
    - _Requirements: 2.1, 2.2, 3.2_
  
  - [ ] 17.5 Create creative studio page
    - Implement /creative-studio page
    - Add creative upload and quality scoring
    - Add creative variant generation interface
    - Display quality scores and improvement suggestions
    - _Requirements: 9.1, 9.2, 11.1, 11.4_
  
  - [ ] 17.6 Create analytics pages
    - Implement /analytics/attribution page for multi-touch attribution
    - Implement /analytics/bias-audit page for fairness analysis
    - Implement /analytics/budget-simulator page
    - _Requirements: 10.1, 12.1, 13.1_
  
  - [ ] 17.7 Create settings page
    - Implement /settings page for organization and user management
    - Add user invitation functionality
    - _Requirements: 1.2_

- [ ] 18. Set up AWS infrastructure
  - [ ] 18.1 Create VPC and security groups
    - Create VPC with public and private subnets
    - Configure security groups for EC2 and RDS
    - _Requirements: All_
  
  - [ ] 18.2 Launch RDS PostgreSQL instance
    - Create db.t3.micro instance
    - Configure backup and encryption
    - _Requirements: All database requirements_
  
  - [ ] 18.3 Create S3 buckets
    - Create advision-creatives, advision-models, advision-uploads buckets
    - Configure encryption and lifecycle policies
    - _Requirements: 2.2, 14.1_
  
  - [ ] 18.4 Set up Secrets Manager
    - Store database credentials, JWT secret, OpenAI API key
    - _Requirements: All_
  
  - [ ] 18.5 Create IAM roles and policies
    - Create EC2 instance role with S3, RDS, Secrets Manager access
    - _Requirements: All_
  
  - [ ] 18.6 Launch EC2 instance
    - Launch t3.medium instance with Docker
    - Attach IAM role and security group
    - _Requirements: All_

- [ ] 19. Deploy application to AWS
  - [ ] 19.1 Configure environment variables
    - Fetch secrets from Secrets Manager
    - Create .env file with all required variables
    - _Requirements: All_
  
  - [ ] 19.2 Build and push Docker images
    - Build frontend, backend, ml-service images
    - Test locally with docker-compose
    - _Requirements: All_
  
  - [ ] 19.3 Deploy to EC2
    - SSH into EC2 instance
    - Clone repository and run docker-compose up
    - _Requirements: All_
  
  - [ ] 19.4 Run database migrations
    - Execute Alembic migrations on RDS
    - Verify all tables created
    - _Requirements: All database requirements_
  
  - [ ] 19.5 Upload ML models to S3
    - Download pretrained models (CLIP, DistilBERT, etc.)
    - Upload to S3 with proper versioning
    - Update model registry
    - _Requirements: 14.1, 14.2_

- [ ] 20. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
