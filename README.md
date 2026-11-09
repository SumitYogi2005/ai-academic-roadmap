# 🎓 AI Academic Roadmap

> Transform your academic syllabus into an interactive, personalized learning journey powered by AI.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=flat&logo=mongodb)](https://www.mongodb.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://python.org)

## 📖 Overview

AI Academic Roadmap is a personalized learning platform that converts institutional syllabi and skill-development goals into structured, interactive roadmaps. It creates study schedules based on a student's available time, learning level, goals, and deadlines.

### Key Features

- **📄 Syllabus Upload** — Upload PDF, DOCX, JPG, or PNG syllabus files for automatic AI extraction
- **🗺️ Interactive Roadmap** — Visualize learning paths as an interactive graph with prerequisite connections
- **📅 Smart Study Planner** — Algorithmic scheduling that respects daily capacity, prerequisites, and deadlines
- **🤖 AI Assistant** — Context-aware explanations, notes, and quizzes for every topic
- **📊 Progress Analytics** — Track completion, study time, and learning pace
- **✏️ Skill Mode** — Generate custom learning roadmaps for any skill from beginner to advanced

## 🏗️ Architecture

```
┌─────────────────┐    HTTPS/REST/JSON    ┌──────────────────────────┐
│   React + Vite  │ ◄──────────────────► │      FastAPI Backend      │
│   Frontend      │                       │                           │
│                 │                       │  ├── Auth & User APIs     │
│  - React Flow   │                       │  ├── Document APIs        │
│  - Zustand      │                       │  ├── Roadmap APIs         │
│  - TanStack Q   │                       │  ├── Planner APIs         │
│  - Tailwind CSS │                       │  └── AI Assistant APIs    │
└─────────────────┘                       └──────────────┬────────────┘
                                                         │
                                          ┌──────────────┼────────────┐
                                          │              │            │
                                     ┌────▼────┐  ┌─────▼─────┐  ┌──▼──────┐
                                     │ MongoDB │  │   Local   │  │  LLM    │
                                     │   DB    │  │  Storage  │  │   API   │
                                     └─────────┘  └───────────┘  └─────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **MongoDB** 7.0+ (local or Atlas)
- **Tesseract OCR** (optional, for scanned PDFs/images)
- An **OpenAI API key** (or compatible LLM API)

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd ai-academic-roadmap
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings (MongoDB URL, AI API key, etc.)

# Start the backend
uvicorn app.main:app --reload
# → Running at http://localhost:8000
# → API docs at http://localhost:8000/docs
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
# → Running at http://localhost:5173
```

### 4. Configure `.env`

Edit `backend/.env`:

```env
SECRET_KEY=your-secret-key-at-least-32-characters-long
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=ai_academic_roadmap
AI_API_KEY=sk-your-openai-api-key
AI_MODEL=gpt-4o-mini
```

## 📁 Project Structure

```
ai-academic-roadmap/
├── frontend/
│   └── src/
│       ├── components/        # Shared UI components
│       │   ├── layout/        # AppSidebar, AppHeader, AppLayout
│       │   └── ui/            # Button, Input, Modal, Badge, etc.
│       ├── features/          # Feature modules
│       │   ├── landing/       # Landing page
│       │   ├── auth/          # Login & Register
│       │   ├── onboarding/    # Student setup
│       │   ├── dashboard/     # Main dashboard
│       │   ├── roadmaps/      # Roadmap list, create, viewer
│       │   ├── syllabus/      # Document upload & review
│       │   ├── planner/       # Study calendar
│       │   ├── assistant/     # AI chat interface
│       │   ├── analytics/     # Progress charts
│       │   └── settings/      # User preferences
│       ├── hooks/             # Custom React hooks (API calls)
│       ├── lib/               # Axios instance, Query client
│       └── store/             # Zustand state stores
├── backend/
│   ├── app/
│   │   ├── api/routes/        # FastAPI route handlers
│   │   ├── core/              # Config, security, logging
│   │   ├── db/                # MongoDB client & indexes
│   │   ├── models/            # MongoDB document models
│   │   ├── repositories/      # Database access layer
│   │   ├── schemas/           # Pydantic request/response
│   │   └── services/
│   │       ├── ai/            # LLM provider abstraction
│   │       ├── document/      # File extraction & storage
│   │       ├── roadmap/       # Roadmap generation
│   │       └── planner/       # Study schedule algorithm
│   ├── uploads/               # Stored documents (gitignored)
│   └── tests/
├── docs/
├── docker-compose.yml
└── README.md
```

## 🗄️ Database Design

### Collections

| Collection | Purpose |
|------------|---------|
| `users` | Student accounts and embedded preferences |
| `syllabus_documents` | Uploaded file metadata and processing status |
| `syllabus_content` | Extracted units, topics, and subtopics |
| `roadmaps` | Roadmap metadata (academic or skill mode) |
| `roadmap_nodes` | Individual learning nodes with difficulty/duration |
| `roadmap_edges` | Prerequisite and related-topic connections |
| `study_plans` | Generated study plan metadata |
| `study_sessions` | Individual daily study sessions |
| `topic_progress` | Per-student, per-node progress tracking |
| `learning_resources` | Topic-related resource links |
| `assessments` | Quiz questions per topic |
| `assessment_attempts` | Student quiz results |
| `ai_generation_jobs` | AI job audit and retry tracking |

## 🤖 AI & Automation

The AI subsystem uses a **provider abstraction layer** supporting OpenAI-compatible APIs.

### Workflows

1. **Syllabus Analysis** — Extracts units, topics, subtopics from document text; returns validated structured JSON
2. **Academic Roadmap** — Generates learning nodes with AI descriptions and validates prerequisite order
3. **Skill Roadmap** — Creates staged concept → practice → project → assessment progression
4. **Study Planner** — **100% algorithmic** (no LLM); respects capacity, prerequisites, deadlines
5. **AI Tutor** — Context-aware answers grounded in the student's syllabus
6. **Quiz & Notes** — Structured quiz questions and study notes per topic

### Document Processing Pipeline

```
Upload → Validate → Store → Extract → Normalize → AI Analyze → Validate → Student Review → Persist
```

## 📡 API Reference

Full interactive API documentation is available at **http://localhost:8000/docs** when running.

### Key Endpoints

```
POST /api/v1/auth/register          Register student account
POST /api/v1/auth/login             Sign in, receive JWT

GET  /api/v1/users/me               Get current user profile
PUT  /api/v1/users/preferences      Update study preferences

POST /api/v1/documents/upload       Upload syllabus (PDF/DOCX/image)
GET  /api/v1/documents/{id}/status  Check extraction progress
GET  /api/v1/documents/{id}/extraction  Read extracted content
PUT  /api/v1/documents/{id}/extraction  Save student corrections

POST /api/v1/roadmaps/academic      Generate academic roadmap
POST /api/v1/roadmaps/skill         Generate skill roadmap
GET  /api/v1/roadmaps               List all roadmaps
GET  /api/v1/roadmaps/{id}          Get roadmap with nodes/edges

POST /api/v1/study-plans/generate   Create personalized study plan
POST /api/v1/study-plans/{id}/reschedule  Reschedule remaining tasks
PUT  /api/v1/progress/{node_id}     Update topic progress

POST /api/v1/ai/chat                AI learning question
POST /api/v1/ai/quiz                Generate quiz
POST /api/v1/ai/notes               Generate topic notes
```

## 🔒 Security

- Passwords hashed with **Argon2** (via pwdlib)
- **JWT** access + refresh token authentication
- File uploads validated by MIME type, extension, and file signature
- Safe server-side filenames (UUID-based) prevent path traversal
- User **ownership enforced** on every private endpoint
- Document content treated as **untrusted input** for LLM prompts
- CORS allowlist configuration
- Secrets in environment variables, never committed

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

## 🐳 Docker Deployment

```bash
# Start all services (MongoDB, Backend, Frontend)
docker-compose up -d

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🗺️ Roadmap

### MVP (P0 — Required)
- [x] Authentication and student preferences
- [x] PDF/DOCX/image upload and extraction
- [x] Student review of extracted content
- [x] Academic roadmap generation
- [x] Skill roadmap generation
- [x] Interactive roadmap viewer (graph + outline)
- [x] Personalized daily/weekly study planner
- [x] Topic progress tracking

### Portfolio Release (P1)
- [x] AI explanations and Q&A
- [x] Resource suggestions
- [x] Quizzes and auto-generated notes
- [x] Progress analytics dashboard
- [x] Adaptive rescheduling

### Future (P2)
- [ ] Spaced repetition scheduling
- [ ] Syllabus version comparison
- [ ] Collaborative roadmaps
- [ ] Mobile app
- [ ] Google OR-Tools constraint solver integration
- [ ] Institutional/faculty workspace

## 👥 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Built as an advanced portfolio project demonstrating full-stack AI application development with React, FastAPI, MongoDB, and LLM integration.
