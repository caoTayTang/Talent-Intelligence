# Talent Intelligence: Full-Stack Implementation Plan

This document outlines the roadmap for evolving the Talent Intelligence platform from a developer-focused console into a production-ready, multi-role recruitment system.

---

## 1. Architectural Overview

The system follows a decoupled architecture using a **Next.js** frontend, a **FastAPI** backend, and a **Celery** worker for AI orchestration.

### Tech Stack
- **Frontend:** Next.js (App Router), Tailwind CSS, TypeScript, Lucide Icons.
- **Backend:** FastAPI, SQLAlchemy (PostgreSQL + pgvector).
- **Asynchronous Task Queue:** RabbitMQ + Celery.
- **Storage:** Cloudflare R2 (S3-compatible) for CVs and transcripts.
- **AI Orchestration:** LangGraph (inside Celery workers).

---

## 2. Authentication & Role-Based Access (RBAC)

### Current State
The API currently provides a `/users` endpoint that creates a database row for a user with a `role` ("hr" or "candidate"). There is no formal session management or JWT logic yet.

### Implementation Strategy
1.  **Authentication & Access Control (Phase 1):**
    *   **Candidate Access:** Public registration and login allowed.
    *   **HR Access:** Restricted. Recruiters cannot "Register" via the public form. They must be pre-created in the database by an administrator or onboarded via a company-specific invite.
    *   **Mock Transition:** For local dev, the login screen will allow logging into *existing* HR accounts, but the registration form will only support the "Candidate" role.
2.  **Directory Routing:**
    - Use Next.js **Route Groups** to separate concerns:
      - `apps/web/app/(auth)/`: Login and registration.
      - `apps/web/app/(dashboard)/hr/`: Protected HR workspace.
      - `apps/web/app/(dashboard)/candidate/`: Protected Candidate workspace.
3.  **Middleware:**
    - Implement a `middleware.ts` to redirect users based on their role and authentication status.

---

## 3. Frontend Implementation Plan

### 3.1 Global State & Data Fetching
- **Auth Provider:** Wraps the app to provide `user` and `logout()` globally.
- **SWR / React Query:** Adopt a hook-based data fetching library for caching, revalidation, and loading states.
  ```typescript
  // Example hook
  const { data: applications, isLoading } = useSWR('/applications?job_id=...', fetcher);
  ```

### 3.2 HR Workflow (Recruiter Portal)
- **Job Creator:** A multi-step form to define Job Descriptions and configure the AI **Screening Rubric** (criteria, weights, and signals).
- **Applicant Tracking System (ATS) Dashboard:**
  - A table/board view of all applications.
  - Sorting by "AI CV Score" or "Assessment Score".
- **Evidence Review UI:**
  - A specialized view for the `detailed_score_json`.
  - Display the "Gap Analysis" and "Rationale" provided by the screening agent.
  - Show a "Confidence Score" for each AI claim.

### 3.3 Candidate Workflow (Applicant Portal)
- **Job Board:** A clean interface to browse open roles.
- **Direct-to-R2 Upload:**
  - UI requests a presigned URL from `/uploads/presign`.
  - Frontend performs a `PUT` request directly to Cloudflare R2 to minimize server load.
  - On success, the frontend notifies the API to create the `Application` record.
- **Assessment Interface:**
  - A distraction-free environment for take-home tests.
  - Supports markdown-rendered questions and rich-text answers.

---

## 4. Backend & Integration Logic

### 4.1 R2 Storage Integration
The API must handle presigned URLs for both **Uploads** (Candidate CVs) and **Downloads** (HR reviewing CVs).
- **Upload Flow:** `POST /uploads/presign` -> Returns `upload_url` and `object_key`.
- **Download Flow:** `GET /uploads/download/{object_key}` -> Returns a temporary signed URL for the browser to view the PDF.

### 4.2 Async Agent Integration (Polling Pattern)
Since agent tasks (CV screening) can take 30-60 seconds:
1.  **Trigger:** `POST /applications` triggers the Celery task.
2.  **Status Check:** The UI polls `GET /applications/{id}`.
3.  **Completion:** Once `status` changes from `pending_cv` to `cv_passed/failed`, the UI reveals the scores.
4.  **Real-time (Future):** Integrate WebSockets or Server-Sent Events (SSE) via FastAPI to push status updates to the UI.

### 4.3 Database Evolution
- **Hiring Quotas / Thresholds:** Update `packages/backend_shared/talent_core/models.py` (`Job` model) to include fields for passing thresholds: `cv_pass_quota` (int), `assessment_pass_quota` (int), and `interview_pass_quota` (int). These will allow HR to specify how many candidates should proceed to the next round. An Alembic migration (`npm run db:generate` / `npm run db:migrate`) will be required.
- **pgvector:** Utilize semantic search to match candidates against JDs beyond simple keyword matching.
- **Audit Logs:** Ensure the `agent_runs` table captures every decision for compliance and debugging.

---

## 5. UI/UX Style Guide
- **Aesthetic:** Minimalist, high-contrast, and professional (inspired by the existing `#f3f5f0` and `#18211d` color palette).
- **Typography:** Sans-serif for UI elements, Monospace for AI-generated data/logs.
- **Components:** Use Radix UI or headless UI primitives for accessible Modals, Tabs, and Selects.

---

## 6. Implementation Roadmap

### Step 1: Foundation
- Scaffold the `/hr` and `/candidate` layouts.
- Set up the `AuthContext` with mock user persistence.
- Standardize the `api` client with better error handling.

### Step 2: HR Jobs & Candidates
- Build the Job Creation form.
- Implement the Applicant Table with real data from `/applications`.
- Build the "Application Detail" view to render the AI screening results.

### Step 3: Candidate Experience
- Build the Public Job Board.
- Implement the R2 upload flow for CVs.
- Create the "My Applications" tracking page.

### Step 4: Assessments & Polish
- Implement the dynamic assessment renderer.
- Add "Invite to Interview" flows (UI triggers for backend state changes).
- Final UI polish and responsive design.

---

## 7. Data Schema Specifications

To ensure compatibility with the AI agents (CV Screening and Test Generation), the following JSON structures must be strictly followed when interacting with the API.

### 7.1 Job Scorecard (`scorecard_json`)
Used by the CV Screening agent to grade candidates.
- **Path:** `POST /jobs` -> `scorecard_json`
- **Schema:**
```json
{
  "criteria": [
    {
      "id": "technical_depth",
      "label": "Technical Depth",
      "weight": 40,
      "signals": ["Python", "FastAPI", "PostgreSQL"]
    },
    {
      "id": "communication",
      "label": "Communication",
      "weight": 20,
      "signals": ["clear writing", "structured thought"]
    }
  ]
}
```

### 7.2 Dynamic Test Configuration (`dynamic_test_config`)
Used by the Test Generation agent to create a customized assessment.
- **Path:** `POST /jobs` -> `dynamic_test_config`
- **Schema:**
```json
{
  "total_points": 100,
  "distribution": {
    "multiple_choice": {
      "count": 5,
      "total_category_points": 50
    },
    "essay": {
      "count": 2,
      "total_category_points": 50
    }
  }
}
```

### 7.3 Generated Test Content (`dynamic_test_content`)
The UI must be able to render this structure when a candidate takes a test. This is generated by the `agent.test_generation` task.
- **Path:** `GET /applications/{id}` -> `dynamic_test_content`
- **Schema:**
```json
{
  "test_title": "Backend Engineering Assessment",
  "time_limit_minutes": 60,
  "questions": [
    {
      "id": "q1",
      "type": "multiple_choice",
      "content": "What is the primary use of pgvector?",
      "points": 10,
      "options": [
        {"label": "A", "text": "Vector storage for RAG"},
        {"label": "B", "text": "Storing large images"},
        {"label": "C", "text": "Managing user sessions"}
      ]
    },
    {
      "id": "q2",
      "type": "essay",
      "content": "Explain the CAP theorem in the context of distributed systems.",
      "points": 25
    }
  ]
}
```

## Phase 4: Cohort-Based Batch Transitions (Current Focus)

To support fair, quota-based recruitment, the system is moving from rolling admissions to cohort-based batch transitions.

### 1. New Status: `cv_screened`
- **Definition**: The AI has completed the screening and evidence verification, but no decision has been made.
- **Worker Update**: `agent.cv_screening` now terminates at `cv_screened` status and no longer triggers test generation automatically.

### 2. The Batch Transition Worker (`process_cohort_advancement`)
- **Ranking**: A specialized worker task that retrieves all `cv_screened` applications for a job and ranks them by `cv_score`.
- **Quota Logic**:
    - Selects the top `N` candidates where `N = job.cv_pass_quota`.
    - Advances these candidates to `cv_passed` and triggers `agent.test_generation`.
    - Transitions the remaining candidates to `cv_failed`.

### 3. Trigger & Automation
- **Manual Trigger**: API endpoint `POST /jobs/{id}/finalize-cv-round` for HR to manually close the round.
- **Scheduled Trigger**: Celery Beat checks for `job.cv_submission_deadline` and auto-runs the batch transition.

### 4. UI Integration
- HR Dashboard displays "CV Screened" candidates with scores.
- HR Job View provides a "Finalize CV Round" button to execute the batch transition.

