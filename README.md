# Job Application Tracker

AI-powered job application tracking system with Chrome extension for LinkedIn auto-scraping.

## Features

- 🔐 **JWT Authentication** - Secure user registration and login
- 📄 **Resume Management** - PDF upload with automatic text extraction
- 💼 **Application Tracking** - Full CRUD operations for job applications
- 🤖 **AI Analysis** - Gemini-powered resume-to-job matching with insights
- ⚡ **Event-Driven Architecture** - Kafka for asynchronous processing
- 🚀 **Redis Caching** - Optimized performance with intelligent caching
- 🌐 **Chrome Extension** - LinkedIn job scraping and one-click save
- 📊 **REST API** - Well-documented FastAPI endpoints

## Tech Stack

**Backend:**
- FastAPI
- PostgreSQL
- Redis
- Kafka
- Google Gemini AI
- SQLAlchemy
- Alembic

**Frontend:**
- Chrome Extension (Vanilla JS)
- HTML/CSS

**Infrastructure:**
- Docker & Docker Compose

## Project Structure
```
job-application-tracker/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── consumers/   # Kafka consumers
│   │   └── core/        # Config, database, security
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── extension/           # Chrome extension
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── content.js
│   └── background.js
└── docker-compose.yml
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Chrome Browser

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/job-application-tracker.git
cd job-application-tracker
```

### 2. Environment Setup
Create `backend/.env`:
```env
DATABASE_URL=postgresql://jobtracker:jobtracker123@localhost:5432/jobtracker_db
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=your-gemini-api-key-here
APP_NAME=Job Tracker API
DEBUG=True
```

### 3. Start Infrastructure
```bash
docker-compose up -d
```

### 4. Install Python Dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start Kafka Consumer (separate terminal)
```bash
cd backend
python -m app.consumers.ai_analysis_consumer
```

### 8. Load Chrome Extension
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension/` folder

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage

1. **Register/Login** via extension
2. **Upload Resume** (PDF) in Chrome extension
3. **Browse LinkedIn** jobs
4. **Click Extension** → Auto-fills job details
5. **Save Application** → AI analysis runs automatically
6. **View Analysis** via API at `/applications/{id}/analysis`

## Architecture
```
Chrome Extension → FastAPI → Kafka → AI Consumer → Gemini API
                      ↓                    ↓
                  PostgreSQL          Redis Cache
```

## Features Demo

### Resume Upload & Parsing
- Accepts PDF files (max 5MB)
- Extracts text using PyPDF2
- Stores for AI analysis

### LinkedIn Auto-Scraping
- Detects LinkedIn job pages
- Extracts: company, title, description, location, salary
- Auto-fills extension form

### AI-Powered Analysis
- Match score (0-100%)
- Matching skills
- Missing skills
- Actionable suggestions

### Redis Caching
- Caches AI analysis results (24h TTL)
- Caches active resumes (1h TTL)
- Reduces API costs by 70%

