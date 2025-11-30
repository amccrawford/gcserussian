# Project Plan: GCSE Language Testing Web Application

## 1. Executive Summary
**Goal:** Transform the existing CLI-based Python language testing tool into a secure, elegant, web-based application.
**Target Audience:** A closed group of authorized students and tutors.
**Core Value:** Provide accessibility via the browser while maintaining the high-quality AI interaction logic already developed. Ensure data persistence for progress tracking and secure access.

## 2. Proposed Architecture & Tech Stack
*   **Backend:** **FastAPI (Python)**.
    *   *Reason:* High performance, native Python support (allows re-use of existing logic), easy integration with AI libraries, automatic API documentation.
*   **Frontend:** **React (TypeScript) + Vite + Tailwind CSS**.
    *   *Reason:* Industry standard for "elegant and clean" interactive UIs. Component-based architecture suits the "Question -> Audio -> Feedback" flow perfectly.
*   **Database:** **PostgreSQL** (Production) / **SQLite** (Development).
    *   *Reason:* Robust relational data storage for users and exam results.
*   **Authentication:** **OAuth2 with JWT (JSON Web Tokens)**.
    *   *Reason:* Standard, secure method for session management.
*   **Storage:** **S3 Compatible Storage** (e.g., AWS S3 or equivalent).
    *   *Reason:* To store transient audio files (questions and responses) if ephemeral local storage is insufficient for concurrency.

---

## 3. Development Phases

### Phase 1: Backend Adaptation & API Design
**Objective:** Decouple core logic from the CLI and expose it via HTTP endpoints.

*   **Task 1.1 (Refactoring):** Refactor `QuestionGenerator`, `TTSGenerator`, and `ResponseAnalyzer` to remove all `print()` statements and local file I/O. They must return objects/binary streams instead.
*   **Task 1.2 (API Setup):** Initialize a FastAPI project.
*   **Task 1.3 (Endpoints):** Create the following endpoints:
    *   `GET /config`: Fetch available themes, topics, and difficulty levels.
    *   `POST /generate`: Accepts `{theme, topic, subtopic, difficulty}`. Returns `{question_text, question_audio_url/base64}`.
    *   `POST /analyze`: Accepts `{audio_file, context_data}`. Returns `{transcription, translation, score, feedback}`.
*   **Task 1.4 (Audio Handling):** Implement logic to stream TTS audio directly to the response and handle `multipart/form-data` for incoming student audio uploads.

### Phase 2: Database & Authentication (Security)
**Objective:** Secure the platform and enable data persistence.

*   **Task 2.1 (Schema Design):**
    *   `Users` table: (id, username, hashed_password, role).
    *   `Sessions` table: (id, user_id, timestamp, theme, difficulty).
    *   `Results` table: (id, session_id, question_text, student_audio_path, score, feedback_json).
*   **Task 2.2 (Auth Implementation):** Implement login logic, password hashing (bcrypt), and JWT token generation.
*   **Task 2.3 (Middleware):** Create dependency functions to ensure only authenticated users can access `/generate` and `/analyze` endpoints.

### Phase 3: Frontend Development (UI/UX)
**Objective:** Build an elegant, user-friendly interface.

*   **Task 3.1 (Scaffolding):** Set up React with Tailwind CSS and `shadcn/ui` (for polished components).
*   **Task 3.2 (Login Flow):** Create a clean Login/Register page that stores the JWT token.
*   **Task 3.3 (Dashboard):** Create a view showing previous results/history for the logged-in user.
*   **Task 3.4 (Exam Config):** Create a "New Session" card allowing selection of Theme, Topic, and **Difficulty Level**.
*   **Task 3.5 (Active Exam View):**
    *   Audio Player component (for the question).
    *   Audio Recorder component (Visualizer + Start/Stop buttons) using MediaRecorder API.
    *   Loading states (skeletons/spinners) while AI is processing.
    *   Feedback display card (clean typography for Score and Suggestions).

### Phase 4: Integration & End-to-End Testing
**Objective:** Connect FE and BE and ensure stability.

*   **Task 4.1 (Wiring):** Connect React state management (e.g., React Query or Zustand) to FastAPI endpoints.
*   **Task 4.2 (Audio Pipeline Test):** Verify that audio recorded in the browser (WebM/Blob) is correctly received, converted (if necessary, e.g., using `ffmpeg`), and processed by the Python backend.
*   **Task 4.3 (Error Handling):** Implement graceful degradation (e.g., "AI service busy", "Microphone permission denied").

### Phase 5: Deployment & Hardening
**Objective:** Make the application accessible online.

*   **Task 5.1 (Containerization):** Create a `Dockerfile` to bundle the Python backend and Frontend static build.
*   **Task 5.2 (Environment):** Set up environment variables (`GEMINI_API_KEY`, `DATABASE_URL`, `SECRET_KEY`) in the hosting provider.
*   **Task 5.3 (Hosting):** Deploy to a PaaS provider (e.g., Render, Railway, or DigitalOcean).
*   **Task 5.4 (Security Audit):** Ensure API keys are not exposed, enforce HTTPS, and disable debug mode.

## 4. Resources Required
*   **Backend Developer:** Proficient in Python, FastAPI, and Async I/O.
*   **Frontend Developer:** Proficient in React, Modern CSS, and handling browser Audio APIs.
*(Note: A strong Full Stack developer could handle both).*

## 5. Timeline Estimate (Draft)
*   **Phase 1:** 3-4 Days
*   **Phase 2:** 2-3 Days
*   **Phase 3:** 4-5 Days
*   **Phase 4:** 2 Days
*   **Phase 5:** 1-2 Days
**Total:** ~2-3 Weeks for MVP.
