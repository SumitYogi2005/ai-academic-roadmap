# System Architecture & Data Flow

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Landing │ │   Auth   │ │Dashboard │ │  Roadmap Viewer  │  │
│  │   Page   │ │  Pages   │ │          │ │  (@xyflow/react) │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │  Syllabus│ │  Study   │ │    AI    │ │    Analytics     │  │
│  │  Review  │ │ Planner  │ │Assistant │ │    Dashboard     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
│                                                                │
│  State: Zustand (client) + TanStack Query (server state)       │
│  Routing: React Router v7                                      │
└───────────────────────────┬────────────────────────────────────┘
                            │ HTTPS/REST/JSON
                            │ JWT Bearer Token
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                           │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  API Layer (app/api/routes/)                           │   │
│  │  auth | users | documents | roadmaps | planner |       │   │
│  │  progress | ai_assistant | health                      │   │
│  └────────────────┬───────────────────────────────────────┘   │
│                   │                                            │
│  ┌────────────────▼───────────────────────────────────────┐   │
│  │  Service Layer (app/services/)                         │   │
│  │                                                        │   │
│  │  document/     │  ai/           │  roadmap/            │   │
│  │  ├─ extractor  │  ├─ provider   │  └─ generator        │   │
│  │  └─ storage    │  └─ prompts    │                      │   │
│  │                │                │  planner/            │   │
│  │                │                │  └─ scheduler        │   │
│  └────────────────┬───────────────────────────────────────┘   │
│                   │                                            │
│  ┌────────────────▼───────────────────────────────────────┐   │
│  │  Repository Layer (app/repositories/)                  │   │
│  │  user_repo | document_repo | roadmap_repo |            │   │
│  │  planner_repo                                          │   │
│  └────────────────┬───────────────────────────────────────┘   │
└───────────────────┼────────────────────────────────────────────┘
                    │
         ┌──────────┼──────────────────┐
         │          │                  │
         ▼          ▼                  ▼
  ┌──────────┐ ┌──────────┐    ┌──────────────┐
  │ MongoDB  │ │  Local   │    │   LLM API    │
  │          │ │  File    │    │  (OpenAI /   │
  │ 13 colls │ │ Storage  │    │ compatible)  │
  └──────────┘ └──────────┘    └──────────────┘
```

## Document Processing Data Flow

```
                    Student uploads PDF/DOCX/Image
                              │
                              ▼
                    ┌─────────────────┐
                    │  File Validation │
                    │  - MIME type    │
                    │  - Extension    │
                    │  - File size    │
                    │  - File sig     │
                    └────────┬────────┘
                             │ Valid
                             ▼
                    ┌─────────────────┐
                    │  Secure Storage │
                    │  - UUID filename│
                    │  - Outside      │
                    │    web root     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Text Extraction│
                    │  PDF → PyMuPDF  │
                    │  DOCX → python- │
                    │         docx    │
                    │  Image → OCR    │
                    │   (Tesseract)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Normalization  │
                    │  - Clean header │
                    │    /footers     │
                    │  - Preserve     │
                    │    structure    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  AI Analysis    │
                    │  - LLM call     │
                    │  - Schema-      │
                    │    constrained  │
                    │    output       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Validation     │
                    │  - Pydantic     │
                    │    schema       │
                    │  - Hierarchy    │
                    │    checks       │
                    │  - Duplicate    │
                    │    detection    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Student Review │
                    │  - Edit units   │
                    │  - Edit topics  │
                    │  - Confirm      │
                    └────────┬────────┘
                             │ Confirmed
                             ▼
                    ┌─────────────────┐
                    │ Roadmap         │
                    │ Generation      │
                    └─────────────────┘
```

## Study Plan Scheduling Algorithm

```
Input:
  - roadmap_nodes (with duration_hours, difficulty)
  - roadmap_edges (prerequisites)
  - start_date, target_date
  - availability (day → minutes)

Algorithm:
  1. Calculate available_minutes = sum of daily slots
  2. Calculate required_minutes = sum(node durations) + revision + assessments
  3. If available < required → return infeasibility warning
  4. Build prerequisite graph using edges
  5. Topological sort nodes (prerequisites first)
  6. For each day from start_date to target_date:
     a. Find remaining capacity for this day
     b. Find all nodes whose prerequisites are complete
     c. Sort by: deadline proximity, difficulty, importance
     d. Allocate sessions until day is full
     e. Split long topics across multiple days
  7. Add revision sessions (10-15% of total time)
  8. Add assessment sessions at unit boundaries
  9. Validate: no day over capacity, prerequisites respected
  10. Save sessions + plan metadata

Output:
  - study_plan (metadata)
  - study_sessions (list of daily sessions)
  - feasibility_report
```

## MongoDB Collection Relationships

```
users (1)
  └── syllabus_documents (N)   [user_id ref]
       └── syllabus_content (1) [document_id ref]
  └── roadmaps (N)             [user_id ref]
       └── roadmap_nodes (N)   [roadmap_id ref]
       └── roadmap_edges (N)   [roadmap_id ref]
  └── study_plans (N)          [user_id, roadmap_id ref]
       └── study_sessions (N)  [plan_id, node_id ref]
  └── topic_progress (N)       [user_id, roadmap_id, node_id ref]
  └── assessment_attempts (N)  [user_id, assessment_id ref]

roadmap_nodes (1)
  └── learning_resources (N)   [node_id ref]
  └── assessments (N)          [node_id ref]

ai_generation_jobs (N)        [user_id, document_id ref]
```
