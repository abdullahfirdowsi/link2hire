# Link2Hire - Intelligent LinkedIn Job Processing System

> **Production-ready AI system that extracts structured job data from unstructured postings and generates professional, algorithm-optimized LinkedIn posts using Azure OpenAI.**

## 🎯 Project Overview

Link2Hire automates and optimizes the entire job posting workflow with intelligent AI agents:

### The Problem It Solves
- ❌ Manual job posting is time-consuming
- ❌ Random post formats look spammy and get low engagement
- ❌ Inconsistent tone damages credibility
- ❌ No systematic approach to different job types

### The Solution
✅ **Intelligent Classification**: AI automatically categorizes jobs (internship, fresher, remote, etc.)  
✅ **Professional Tone Matching**: Each job type gets an appropriate, algorithm-friendly format  
✅ **Automated Extraction**: Structured data extracted from unstructured text  
✅ **Multi-Role Handling**: Smart detection of multiple positions with clarification workflow  
✅ **Integrated Tracking**: MongoDB + Google Sheets for complete job lifecycle management

### Workflow
```
Unstructured Job Text
    ↓
AI Extraction → Structured Data (company, roles, location, salary)
    ↓
Intelligent Classification → Job Category Detection
    ↓
Professional Tone Selection → Algorithm-Optimized Format
    ↓
LinkedIn Post Generation → Trust-Building Content
    ↓
Multi-Channel Storage → MongoDB + Google Sheets
```

### Results
- **Before**: 11 posts/25 minutes → 2-28 impressions per post (spam-flagged)
- **After**: 3 strategic posts/day → 300-600 impressions per post (professional growth)

## 🏗️ Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Angular 17 + Tailwind CSS | Modern, responsive chat UI |
| **Backend** | Python FastAPI | High-performance API server |
| **AI/LLM** | Azure OpenAI (GPT-4) | Intelligent extraction & classification |
| **Database** | MongoDB Atlas | Job data persistence |
| **Tracking** | Google Sheets API | External tracking & reporting |
| **Infrastructure** | Docker + Docker Compose | Containerized deployment |

### Intelligent AI Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                       │
│          (Coordinates entire workflow)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                   ↓
┌──────────────┐  ┌─────────────────┐  ┌──────────────┐
│  EXTRACTOR   │  │   CLASSIFIER    │  │   DECISION   │
│   Extract    │  │  Categorize job │  │ Multi-role   │
│  structured  │  │  (internship,   │  │ detection &  │
│    data      │  │  fresher, etc.) │  │clarification │
└──────────────┘  └─────────────────┘  └──────────────┘
        ↓                  ↓                   ↓
        └──────────────────┼───────────────────┘
                            ↓
                   ┌────────────────┐
                   │   FORMATTER    │
                   │  Professional  │
                   │ tone-matched   │
                   │  LinkedIn post │
                   └────────────────┘
                            ↓
                   ┌────────────────┐
                   │   VALIDATOR    │
                   │ Quality checks │
                   └────────────────┘
                            ↓
              ┌─────────────┴─────────────┐
              ↓                           ↓
    ┌──────────────────┐      ┌──────────────────┐
    │  MongoDB Service │      │  Sheets Service  │
    │   (Persistence)  │      │   (Tracking)     │
    └──────────────────┘      └──────────────────┘
```

### Job Classification System

The AI automatically categorizes jobs and selects appropriate tone:

| Job Category | When Detected | Post Tone | LinkedIn Strategy |
|-------------|---------------|-----------|-------------------|
| **Internship** | "intern" keywords | Informational | Clean facts, eligibility focus |
| **Fresher Hiring** | Entry-level, 0 experience | Alert | Opportunity highlight |
| **Remote Job** | WFH, remote keywords | Benefits | Flexibility emphasis |
| **Mass Hiring** | 100+ positions | Professional Urgent | Scale without spam |
| **Startup Job** | Startup, growth-stage | Innovation | Impact & learning focus |
| **Paid Internship** | High stipend (>15k) | Compensation | Monetary value highlight |

**Example Classification:**
```python
Input: "TechCorp hiring 200 SDE freshers, WFH, 8 LPA"
→ AI detects: MASS_HIRING + REMOTE_JOB + FRESHER_HIRING
→ Selects: Professional Urgent tone with remote benefits
→ Generates: Trust-building post (not spammy)
```

### Project Structure

```
link2hire-v1/
├── backend/
│   ├── agent/
│   │   ├── orchestrator.py         # Master workflow coordinator
│   │   ├── extractor.py            # AI data extraction
│   │   ├── classifier.py           # 🆕 Intelligent job categorization
│   │   ├── decision.py             # Multi-role detection
│   │   ├── formatter.py            # 🆕 Tone-matched post generation
│   │   ├── professional_styles.py  # 🆕 6 professional templates
│   │   ├── post_styles.py          # Legacy 10-style system
│   │   └── validator.py            # Data quality validation
│   ├── services/
│   │   ├── mongodb_service.py      # Job persistence
│   │   ├── sheets_service.py       # External tracking
│   │   └── linkedin_service.py     # LinkedIn API integration
│   ├── models/
│   │   └── job_model.py            # Pydantic schemas
│   ├── utils/
│   │   └── helpers.py              # Utilities
│   ├── config.py                   # Settings management
│   ├── main.py                     # FastAPI application
│   └── requirements.txt            # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/chat/    # Chat interface
│   │   │   ├── services/           # API services
│   │   │   └── models/             # TypeScript models
│   │   └── environments/           # Config
│   └── [Angular config files]
│
├── docker-compose.yml              # Multi-container orchestration
├── ARCHITECTURE_IMPROVEMENTS.md    # Architecture documentation
├── POSTING_STRATEGY.md             # LinkedIn growth strategy
├── LINKEDIN_STYLES_GUIDE.md        # Post style reference
└── README.md                       # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **MongoDB Atlas** account ([free tier available](https://www.mongodb.com/cloud/atlas))
- **Azure OpenAI** API access ([request access](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service))
- **Google Cloud** project with Sheets API enabled
- **Git**

### Quick Start (Recommended - Docker)

The fastest way to run the entire stack:

```bash
# 1. Clone repository
git clone <repository-url>
cd link2hire-v1

# 2. Create .env file in backend directory
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

# 3. Add Google Sheets credentials
# Download JSON from Google Cloud Console
# Save to: backend/credentials/sheets-credentials.json

# 4. Start all services
docker-compose up --build

# Access the application:
# Frontend: http://localhost:4200
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Backend Setup (Development)

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Create .env file
   cp .env.example .env
   ```

   **Required `.env` variables:**
   ```env
   # Azure OpenAI
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_api_key
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_API_VERSION=2024-02-15-preview

   # MongoDB
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGODB_DATABASE=link2hire

   # Google Sheets (optional - set to "false" if not using)
   ENABLE_GOOGLE_SHEETS=true
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id

   # API Configuration
   API_CORS_ORIGINS=["http://localhost:4200"]
   DEBUG=true
   ```

4. **Create Google Sheets credentials:**
   ```bash
   mkdir -p credentials
   # Download service account JSON from Google Cloud Console
   # Save to: credentials/sheets-credentials.json
   ```

   **How to get Google Sheets credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a project
   - Enable Google Sheets API
   - Create a service account
   - Download JSON key
   - Share your spreadsheet with the service account email

5. **Run backend:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

   Backend available at: `http://localhost:8000`  
   API docs: `http://localhost:8000/docs`

### Frontend Setup (Development)

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure API URL (optional):**
   
   Edit `src/environments/environment.ts`:
   ```typescript
   export const environment = {
     production: false,
     apiUrl: 'http://localhost:8000'  // Backend URL
   };
   ```

3. **Run development server:**
   ```bash
   npm start
   # or
   ng serve
   ```

   Frontend available at: `http://localhost:4200`

4. **Build for production:**
   ```bash
   npm run build
   # Output: dist/frontend/
   ```

## 📋 API Documentation

### Core Endpoints

#### 1. **Process Job Posting** 
The main endpoint that starts the workflow.

```http
POST /process-job
Content-Type: application/json

Request:
{
  "raw_job_text": "TechCorp is hiring 200 SDE freshers. Remote, 8 LPA. Apply at careers.techcorp.com",
  "user_context": {}
}

Response (Success):
{
  "success": true,
  "message": "✅ Job processed successfully!",
  "conversation_id": "conv_abc123",
  "state": "completed",
  "job_entry": {
    "job_id": "job_2024_001",
    "company_name": "TechCorp",
    "job_role": "SDE Fresher",
    "location": "Remote",
    "salary": "8 LPA"
  },
  "linkedin_post": {
    "post_text": "🌍 Remote Job Opportunity!\n\nTechCorp is hiring SDE Freshers...",
    "hashtags": ["hiring", "remotejobs", "fresherjobs"],
    "classification": "REMOTE_JOB",
    "tone": "Benefits-focused"
  }
}

Response (Clarification Needed):
{
  "success": true,
  "message": "Clarification needed before proceeding.",
  "conversation_id": "conv_abc123",
  "state": "awaiting_clarification",
  "requires_clarification": true,
  "clarification_message": "Detected 3 different roles. Would you like to:\n1. Create separate entries\n2. Create combined entry",
  "detected_roles": [
    "Frontend Developer",
    "Backend Developer", 
    "Full Stack Developer"
  ]
}
```

#### 2. **Submit Clarification Response**
Used when multiple roles are detected.

```http
POST /clarification-response
Content-Type: application/json

Request:
{
  "conversation_id": "conv_abc123",
  "choice": "separate"  // or "combined"
}

Response:
{
  "success": true,
  "message": "✅ Successfully processed 3 job entries!",
  "conversation_id": "conv_abc123",
  "state": "completed",
  "job_entries_created": ["job_001", "job_002", "job_003"],
  "linkedin_posts": [
    {
      "job_id": "job_001",
      "post_text": "...",
      "classification": "INTERNSHIP"
    }
  ]
}
```

#### 3. **Get Conversation Status**
Retrieve conversation state and history.

```http
GET /conversation/{conversation_id}

Response:
{
  "conversation_id": "conv_abc123",
  "state": "completed",
  "created_at": "2024-03-05T10:30:00Z",
  "job_entries": ["job_001", "job_002"],
  "linkedin_posts_generated": 2
}
```

#### 4. **Health Check**
Verify service status and dependencies.

```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-03-05T10:30:00Z",
  "services": {
    "mongodb": "connected",
    "azure_openai": "available",
    "google_sheets": "connected"
  },
  "version": "1.0.0"
}
```

### Response Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | Success | Request processed successfully |
| 201 | Created | New resource created |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error occurred |
| 503 | Service Unavailable | External service (Azure OpenAI, MongoDB) down |

## ✨ Key Features

### 1. Intelligent Job Classification
- **Automatic categorization** of 6+ job types
- **Heuristic + LLM hybrid** approach for accuracy
- **Fallback logic** when LLM unavailable
- **Context-aware** detection (salary, keywords, company type)

### 2. Professional Post Generation
- **Tone-matched templates** for each job category
- **Algorithm-optimized** formatting (no spam flags)
- **Consistent branding** with profile integration
- **Hashtag intelligence** based on job context

### 3. Multi-Role Handling
- **Automatic detection** of multiple positions
- **User clarification** workflow
- **Batch processing** for separate entries
- **Combined entry** option for similar roles

### 4. Data Validation & Quality
- **Schema validation** with Pydantic
- **Required fields** enforcement
- **Data sanitization** and cleaning
- **Error handling** with helpful messages

### 5. Multi-Channel Storage
- **MongoDB** for primary persistence
- **Google Sheets** for external tracking
- **Atomic operations** ensure data consistency
- **Rollback capability** on failures

### 6. Production-Ready Infrastructure
- **Docker containerization** for easy deployment
- **CORS configuration** for frontend integration
- **Structured logging** for debugging
- **Health checks** for monitoring
- **Environment-based** configuration

## 📊 LinkedIn Posting Strategy

### The Problem We Solved
**Before:** 11 posts in 25 minutes → 2-28 impressions per post (spam-flagged)  
**After:** 3 strategic posts/day → 300-600 impressions per post (professional growth)

### Recommended Schedule

```
Daily Posting Times (3 posts/day):

9:00 AM  - Primary Morning Post
├─ Target: College students checking phones before class
├─ Content: Internship or fresher role
└─ Expected: 300-500 impressions

1:00 PM  - Mid-Day Update
├─ Target: Lunch break audience
├─ Content: Remote job or paid internship
└─ Expected: 250-400 impressions

6:00 PM  - Evening Opportunity
├─ Target: Evening job searchers
├─ Content: Startup role or mass hiring
└─ Expected: 300-600 impressions

Weekly Total: 15,000-21,000 impressions
Monthly Total: 60,000-90,000 impressions
```

### Growth Roadmap

| Timeline | Goal | Strategy |
|----------|------|----------|
| **Week 1-2** | 50-100 followers | Foundation building, consistency |
| **Month 1** | 200-300 followers | Community engagement, 3 posts/day |
| **Month 2** | 500-1,000 followers | Partnerships, content variety |
| **Month 3+** | 1,000+ followers | Thought leadership, organic growth |

See [POSTING_STRATEGY.md](POSTING_STRATEGY.md) for detailed weekly plans.

### Content Quality Guidelines

✅ **Do:**
- Use professional, trust-building language
- Match tone to job type (informational, alert, benefits)
- Include clear call-to-action
- Add 3-5 relevant hashtags
- Engage with comments within 2 hours

❌ **Don't:**
- Use excessive emojis or marketing hype
- Post more than 3 times per day
- Rotate randomly through templates
- Use phrases like "GOLDEN", "MASSIVE", "THE opportunity"
- Ignore audience engagement

## 🧪 Testing
{
  "conversation_id": "conv_abc123",
  "state": "completed",
  "raw_input": "...",
  "extracted_data": {...},
  "job_entry_ids": ["job_001"]
}
```

#### 4. **Get Jobs by Conversation**
```http
GET /jobs/{conversation_id}

Response:
{
  "conversation_id": "conv_abc123",
  "count": 1,
  "jobs": [...]
}
```

#### 5. **Health Check**
```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-03-03T10:00:00",
  "services": {
    "azure_openai": true,
    "mongodb": true,
    "google_sheets": true
  }
}
```

## 🧠 Agent Architecture

### Agent Pattern

Each agent is a specialized component focusing on a single responsibility:

```
User Input
    ↓
[Extraction Agent] → Extract structured data from raw text
    ↓
[Validation Agent] → Check data quality and completeness
    ↓
[Decision Agent]   → Determine if clarification needed
    ↓
    ├─ If clarification needed → Wait for user
    │
    └─ If no clarification → Proceed to execution
        ↓
    [Formatter Agent]    → Generate LinkedIn post
    ↓
    [Services Layer]     → Save to MongoDB & Google Sheets
    ↓
    Response to User
```

### Agent Modules

#### **ExtractorAgent** (`agent/extractor.py`)
- Uses Azure OpenAI with temperature=0 for deterministic output
- Returns strict JSON schema matching `ExtractedJobData` model
- Detects multiple roles in a single posting
- Uses system prompt to enforce format

#### **DecisionAgent** (`agent/decision.py`)
- Analyzes extracted data against business rules
- Determines if > 1 role detected
- Checks for missing required fields
- Returns decision with clarification message

#### **FormatterAgent** (`agent/formatter.py`)
- Generates engaging LinkedIn post content
- Extracts hashtags from generated text
- Fallback to simple template if AI fails
- Uses temperature=0.7 for creative content

#### **ValidationAgent** (`agent/validator.py`)
- Validates URL format and structure
- Checks for placeholder/invalid values
- Calculates data quality score
- Reports validation errors for user review

#### **JobProcessingOrchestrator** (`agent/orchestrator.py`)
- Central coordinator managing entire workflow
- Maintains conversation state in MongoDB
- Coordinates agent execution sequentially
- Handles error recovery and state transitions
- Manages service layer interactions

### Service Layer

#### **MongoDBService** (`services/mongodb_service.py`)
- Async MongoDB operations using Motor
- Manages conversations and job entries
- Creates indexes for performance
- Provides CRUD operations with logging

#### **GoogleSheetsService** (`services/sheets_service.py`)
- Service account authentication
- Appends job entries to tracking spreadsheet
- Updates LinkedIn posting status
- Retrieves historical entries

#### **LinkedInService** (`services/linkedin_service.py`)
- Placeholder for future LinkedIn API integration
- OAuth 2.0 authentication framework
- Post scheduling architecture
- Analytics retrieval interface

## 🧪 Testing

### Available Test Scripts

The project includes several test scripts in the root directory:

```bash
# Test job classification (heuristic + LLM)
python test_classification.py

# Test heuristic-only classification
python test_heuristic_classification.py

# Test professional post styles
python test_professional_styles.py

# Test style comparison (old vs new)
python test_style_comparison.py

# Quick integration test
python quick_test.py
```

### Manual Testing

#### 1. Test Extraction Agent
```bash
# Navigate to backend directory
cd backend

# Test with debug endpoint
curl "http://localhost:8000/debug/test-extraction?text=TechCorp%20hiring%20SDE%20intern%2030k%20stipend"
```

#### 2. Test Job Classification
```python
# In Python console
from backend.agent.classifier import JobClassifier

classifier = JobClassifier()
text = "Hiring 200 SDE freshers, remote, 8 LPA"
category = await classifier.classify_job(text, {})

print(f"Category: {category}")
# Expected: MASS_HIRING or REMOTE_JOB
```

#### 3. Test Full Workflow
```bash
# 1. Process job
curl -X POST http://localhost:8000/process-job \
  -H "Content-Type: application/json" \
  -d '{
    "raw_job_text": "Amazon hiring Software Development Engineer Intern. Bangalore. 50k stipend. Apply at amazon.jobs"
  }'

# 2. Get conversation (use ID from response)
curl http://localhost:8000/conversation/{conversation_id}

# 3. Submit clarification (if required)
curl -X POST http://localhost:8000/clarification-response \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "choice": "separate"
  }'
```

#### 4. Test LinkedIn Post Generation
```python
# Test professional styles
from backend.agent.professional_styles import ProfessionalStyleSelector
from backend.agent.classifier import JobCategory

selector = ProfessionalStyleSelector()

# Test internship format
post = selector.get_style_for_category(JobCategory.INTERNSHIP)
print(post.format(
    company_name="Google",
    job_role="Software Engineer Intern",
    location="Bangalore",
    formatted_salary="INR 80,000/month",
    work_mode="Hybrid",
    apply_link="google.com/careers"
))
```

### Integration Testing

```bash
# Using the Angular frontend
cd frontend
npm start

# Then in browser:
# 1. Navigate to http://localhost:4200
# 2. Paste test job posting
# 3. Verify extraction accuracy
# 4. Check clarification workflow
# 5. Verify LinkedIn post format
# 6. Confirm MongoDB/Sheets storage
```

### Sample Test Cases

#### Test Case 1: Single Internship
```
Input: "Google hiring SDE intern, Bangalore, 80k/month, 2025 graduates"
Expected:
  - Classification: PAID_INTERNSHIP
  - Tone: Compensation-focused
  - LinkedIn post: Professional, highlights stipend
```

#### Test Case 2: Mass Hiring
```
Input: "TCS mega hiring drive: 500+ positions for freshers across India"
Expected:
  - Classification: MASS_HIRING
  - Tone: Professional urgent
  - LinkedIn post: Scale-focused, not spammy
```

#### Test Case 3: Multiple Roles
```
Input: "Startup hiring: Frontend, Backend, Full Stack developers"
Expected:
  - Clarification required: true
  - Detected roles: 3
  - Options: combined/separate
```

## 🔄 Processing Workflow

### How the AI Agents Work Together

```mermaid
graph TD
    A[User Input] -->|Raw Job Text| B[ExtractorAgent]
    B -->|Structured Data| C[ValidatorAgent]
    C -->|Quality Check| D[DecisionAgent]
    D -->|Multi-role?| E{Clarification?}
    E -->|Yes| F[Wait for User]
    E -->|No| G[ClassifierAgent]
    F -->|User Choice| G
    G -->|Job Category| H[FormatterAgent]
    H -->|Tone-matched Post| I[MongoDBService]
    I -->|Save| J[GoogleSheetsService]
    J -->|Track| K[Return Results]
```

### State Machine

```
INITIAL
  ↓
[ExtractorAgent] Extract structured data
  ↓
[DecisionAgent] Check for multiple roles
  ↓
AWAITING_CLARIFICATION (if multiple roles detected)
  ↓ (user responds with choice)
[ClassifierAgent] Categorize job type
  ↓
[FormatterAgent] Generate professional post
  ↓
PROCESSING (save to databases)
  ↓
COMPLETED ✅ (success) or ERROR ❌ (failure)
```

### Classification Decision Tree

```
Job Text Input
    ↓
Is "intern" in text?
    ├─ Yes + High Stipend (>15k)
    │   → PAID_INTERNSHIP (Compensation tone)
    └─ Yes + Lower Stipend
        → INTERNSHIP (Informational tone)
    ↓
Is count > 100?
    → MASS_HIRING (Professional urgent tone)
    ↓
Is "remote" or "WFH"?
    → REMOTE_JOB (Benefits tone)
    ↓
Is "startup" or "early-stage"?
    → STARTUP_JOB (Innovation tone)
    ↓
Is entry-level (0 experience)?
    → FRESHER_HIRING (Alert tone)
    ↓
Default
    → UNKNOWN (Generic professional tone)
```

## 🏛️ Architecture Deep Dive

### Agent Layer

#### **ExtractorAgent** ([agent/extractor.py](backend/agent/extractor.py))
- Uses Azure OpenAI GPT-4 for intelligent extraction
- Few-shot learning with example prompts
- Structured output via Pydantic models
- Handles missing/partial data gracefully
- Temperature=0 for consistent results

#### **ClassifierAgent** ([agent/classifier.py](backend/agent/classifier.py)) 🆕
- **Hybrid approach**: Heuristic fallback + LLM intelligence
- Categorizes jobs into 6 types
- Context-aware detection (salary, keywords, count)
- Handles edge cases (e.g., "paid intern" vs "intern")

#### **DecisionAgent** ([agent/decision.py](backend/agent/decision.py))
- Detects multiple job roles in single posting
- Identifies missing critical fields
- Generates clarification messages
- Coordinates user interaction workflow

#### **FormatterAgent** ([agent/formatter.py](backend/agent/formatter.py)) 🆕
- **Intelligent tone selection** based on classification
- 6 professional templates (not random rotation)
- Algorithm-optimized formatting
- Consistent branding with profile info
- Automatic hashtag extraction

#### **ValidationAgent** ([agent/validator.py](backend/agent/validator.py))
- URL format validation
- Placeholder detection ("TBD", "NA")
- Data quality scoring
- User-friendly error messages

#### **Orchestrator** ([agent/orchestrator.py](backend/agent/orchestrator.py))
- Master workflow coordinator
- Maintains conversation state
- Error recovery and rollback
- Service layer orchestration

### Service Layer

#### **MongoDBService** ([services/mongodb_service.py](backend/services/mongodb_service.py))
- Async operations with Motor
- Conversation and job persistence
- Index management for performance
- CRUD with structured logging

#### **GoogleSheetsService** ([services/sheets_service.py](backend/services/sheets_service.py))
- Service account authentication
- Job tracking in external spreadsheet
- Status updates (posted/not posted)
- Historical entry retrieval

#### **LinkedInService** ([services/linkedin_service.py](backend/services/linkedin_service.py))
- Placeholder for future LinkedIn API
- OAuth 2.0 framework ready
- Post scheduling architecture
- Analytics retrieval interface

## � Database Schema

### Conversations Collection (MongoDB)
```python
{
  "_id": ObjectId,
  "conversation_id": str,        # Unique conversation ID (conv_xxx)
  "state": str,                  # INITIAL | AWAITING_CLARIFICATION | PROCESSING | COMPLETED | ERROR
  "raw_input": str,              # Original user input text
  "extracted_data": {            # ExtractedJobData model
    "company_name": str,
    "job_roles": [str],
    "location": str,
    "work_mode": str,
    "salary": str,
    "application_link": str,
    "additional_details": str
  },
  "decision_output": {           # DecisionOutput model
    "requires_clarification": bool,
    "clarification_reason": str,
    "clarification_message": str,
    "detected_roles": [str]
  },
  "user_choice": str,            # "combined" | "separate" | null
  "job_entry_ids": [str],        # Created job IDs
  "created_at": datetime,
  "updated_at": datetime
}
```

### Jobs Collection (MongoDB)
```python
{
  "_id": str,                    # Unique job ID (job_YYYY_NNN)
  "conversation_id": str,        # Parent conversation
  "raw_input": str,              # Original posting text
  "extracted_data": {...},       # ExtractedJobData model
  "classification": str,         # INTERNSHIP | FRESHER_HIRING | REMOTE_JOB | etc.
  "linkedin_post": {             # LinkedInPost model
    "post_text": str,
    "hashtags": [str],
    "formatted_post": str,
    "tone": str
  },
  "posted_to_sheets": bool,      # Google Sheets sync status
  "posted_to_linkedin": bool,    # LinkedIn API status (future)
  "sheets_row_number": int,      # Row in spreadsheet
  "created_at": datetime,
  "updated_at": datetime
}
```

### Google Sheets Row Format
```
| Column A | Column B | Column C | Column D | Column E | Column F | Column G | Column H |
|----------|----------|----------|----------|----------|----------|----------|----------|
| Job ID   | Company  | Role     | Location | Salary   | Link     | Posted   | Date     |
| job_001  | Google   | SDE      | Bangalore| 80k/mo   | link     | TRUE     | 2024-03-05|
```

## 🔐 Security & Best Practices

### Environment Configuration
- ✅ All credentials in `.env` file (never committed)
- ✅ Service account JSON protected (in `credentials/` directory)
- ✅ CORS restricted to trusted origins
- ✅ MongoDB Atlas IP whitelist configured

### Input Validation
- ✅ Pydantic models enforce type safety
- ✅ Text sanitization (null bytes, trim)
- ✅ URL format validation with regex
- ✅ SQL injection prevention (NoSQL)

### Error Handling
- ✅ Comprehensive exception catching
- ✅ Structured logging with context
- ✅ User-friendly error messages
- ✅ No sensitive data in responses

### Deployment Considerations
```bash
# Production checklist:
- [ ] Set DEBUG=false
- [ ] Use strong MongoDB credentials
- [ ] Enable MongoDB Atlas IP whitelist
- [ ] Rotate Azure OpenAI API keys regularly
- [ ] Monitor API usage/costs
- [ ] Set up error alerting
- [ ] Configure backup strategy
- [ ] Use HTTPS for frontend
```

## 🚨 Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **MongoDB Connection** | `ServerSelectionTimeoutError` | • Check MongoDB URI in `.env`<br>• Whitelist your IP in Atlas<br>• Verify network access |
| **Azure OpenAI 401** | `Unauthorized` | • Verify API key is correct<br>• Check endpoint URL format<br>• Ensure deployment name matches |
| **Google Sheets Fails** | `Permission denied` | • Share spreadsheet with service account email<br>• Grant "Editor" access<br>• Verify credentials JSON path |
| **CORS Errors** | Browser blocks request | • Add frontend URL to `API_CORS_ORIGINS` in backend `.env`<br>• Clear browser cache |
| **Chat Not Loading** | Blank page | • Check both frontend and backend are running<br>• Verify API URL in `environment.ts`<br>• Check browser console |
| **AI Extraction Fails** | Generic/placeholder data | • Check Azure OpenAI quota<br>• Verify deployment is GPT-4<br>• Check input text quality |
| **Classification Wrong** | Incorrect job category | • Review classification logic in `classifier.py`<br>• Test with `test_classification.py`<br>• Check heuristic rules |

### Debug Mode

Enable detailed logging:

```bash
# In backend/.env
DEBUG=true
LOG_LEVEL=DEBUG

# Then restart backend
cd backend
uvicorn main:app --reload --log-level debug
```

View logs in terminal for detailed troubleshooting information.

### Health Check

Verify all services are operational:

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "mongodb": "connected",
    "azure_openai": "available",
    "google_sheets": "connected"
  }
}
```

## 🔮 Future Enhancements

### Phase 1: Core Improvements
- [ ] **LinkedIn API Integration**
  - Direct posting via LinkedIn API
  - OAuth 2.0 authentication
  - Post scheduling
  - Engagement analytics retrieval

- [ ] **Enhanced Classification**
  - More job categories (part-time, contract, etc.)
  - Industry-specific tones
  - Seniority detection (junior, senior, lead)
  - Company size classification

- [ ] **Smart Scheduling**
  - Optimal posting time recommendation
  - Queue management (3 posts/day limit)
  - Automatic spacing between posts

### Phase 2: Analytics & Optimization
- [ ] **Engagement Tracking**
  - Impression counts
  - Click-through rates
  - Which job types perform best
  - A/B testing for post formats

- [ ] **Content Optimization**
  - Hashtag performance analysis
  - Tone effectiveness measurement
  - Post length optimization
  - Emoji usage patterns

- [ ] **Historical Analysis**
  - Job market trends
  - Salary range analysis
  - Popular companies/roles
  - Success rate by category

### Phase 3: Advanced Features
- [ ] **RAG Integration**
  - Company profile context
  - Job description enhancement
  - Similar job suggestions

- [ ] **Multi-Agent Collaboration**
  - Salary verification agent
  - Company credibility checker
  - Location insights agent

- [ ] **Automation**
  - Webhook support for job feeds
  - Automatic RSS ingestion
  - Email-to-job pipeline

- [ ] **Scaling**
  - Celery + Redis for task queue
  - Rate limiting per user
  - GraphQL API option
  - WebSocket for real-time updates

### Phase 4: Enterprise Features
- [ ] **Team Collaboration**
  - User authentication
  - Role-based access
  - Approval workflows
  - Post drafts and reviews

- [ ] **Dashboard**
  - Analytics visualization
  - Job pipeline status
  - Performance metrics
  - Export capabilities

## 📚 Project Documentation

### Key Files

- **[ARCHITECTURE_IMPROVEMENTS.md](ARCHITECTURE_IMPROVEMENTS.md)** - Detailed explanation of the classification system and why it works
- **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)** - Summary of what was fixed and before/after comparison
- **[POSTING_STRATEGY.md](POSTING_STRATEGY.md)** - Month-by-month LinkedIn growth plan
- **[LINKEDIN_STYLES_GUIDE.md](LINKEDIN_STYLES_GUIDE.md)** - Reference guide for post styles
- **[README.md](README.md)** - This file

### Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [MongoDB Motor (Async Driver)](https://motor.readthedocs.io/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Angular Documentation](https://angular.io/docs)

## 📚 Dependencies

### Backend (`requirements.txt`)
```
fastapi>=0.104.0           # Modern web framework
uvicorn[standard]>=0.24.0  # ASGI server
pydantic>=2.5.0            # Data validation
motor>=3.3.0               # Async MongoDB driver
openai>=1.3.0              # Azure OpenAI SDK
gspread>=5.12.0            # Google Sheets API
oauth2client>=4.1.3        # Google OAuth
python-dotenv>=1.0.0       # Environment management
python-multipart>=0.0.6    # File upload support
```

### Frontend (`package.json`)
```json
{
  "@angular/core": "^17.0.0",
  "@angular/common": "^17.0.0",
  "@angular/forms": "^17.0.0",
  "@angular/router": "^17.0.0",
  "tailwindcss": "^3.3.0",
  "rxjs": "^7.8.0",
  "typescript": "~5.2.0"
}
```

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure:
- Code follows existing style conventions
- Tests pass (run test scripts)
- Documentation is updated
- Commit messages are descriptive

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Link2Hire Project**  
Built with ❤️ for intelligent job processing automation

## 📧 Support & Contact

For issues, questions, or suggestions:
- Open a GitHub issue
- Check the troubleshooting section
- Review documentation files

---

## 🎉 Quick Reference

### Start Development
```bash
# Backend (Terminal 1)
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload

# Frontend (Terminal 2)
cd frontend
npm start
```

### Access Points
- Frontend UI: http://localhost:4200
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Key Commands
```bash
# Run all tests
python test_classification.py
python test_professional_styles.py

# Check service health
curl http://localhost:8000/health

# Process a job
curl -X POST http://localhost:8000/process-job \
  -H "Content-Type: application/json" \
  -d '{"raw_job_text": "..."}'
```

---

**Last Updated:** March 2026  
**Version:** 1.0.0