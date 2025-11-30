# Development Plan: Streamlit Migration for GCSE Language App

## Executive Summary
This plan outlines the migration of the existing Python CLI-based Language Testing Tool to a web-based application using **Streamlit**. This approach prioritizes speed of delivery and ease of maintenance while meeting the core requirements of security, user persistence, and accessibility.

**Technical Stack:**
*   **Framework:** Streamlit (Python-only web UI)
*   **Database:** SQLite (with SQLAlchemy ORM)
*   **AI/Logic:** Existing Python Modules (`main.py` logic refactored into services)
*   **Audio:** `streamlit-audiorecorder` (for input) + `st.audio` (for output)

---

## Phase 1: Foundation & Refactoring (Backend Prep)
**Objective:** Decouple the core logic from the CLI `print`/`input` loop so it can be served to a web interface.

### 1.1 Service Layer Extraction
*   **Task:** Create a `services.py` module.
*   **Action:** Move the orchestration logic (getting a theme, generating a question, scoring a response) from `main.py` into pure functions that return objects/dictionaries instead of printing to console.
*   **Deliverable:** `GameEngine` class that manages the state of a single question turn.

### 1.2 Database Integration
*   **Task:** Finalize the Database Schema.
*   **Action:** Ensure `models.py` supports:
    *   **Users:** (Username, Password Hash, Role).
    *   **Sessions:** (User ID, Timestamp, Theme, Score).
    *   **Interactions:** (Audio paths, Transcripts, Feedback).
*   **Deliverable:** A seeded SQLite database with at least 2 test users (Student/Tutor).

---

## Phase 2: The Core Exam Experience (MVP)
**Objective:** Replicate the "Question -> Record -> Feedback" loop in the browser.

### 2.1 Basic Layout & Session State
*   **Task:** Initialize `streamlit_app.py`.
*   **Action:** Setup `st.session_state` to track:
    *   `current_question`
    *   `user_audio`
    *   `analysis_result`
*   **Deliverable:** A page that persists data across button clicks (Streamlit re-runs).

### 2.2 Audio I/O Implementation
*   **Task:** Implement Audio Widgets.
*   **Action:**
    *   Use `st.audio()` to play the generated TTS file.
    *   Integrate `streamlit-audiorecorder` to capture student mic input.
*   **Deliverable:** Functional two-way audio (Machine speaks, User speaks, Audio saved to disk).

### 2.3 Connection to Analysis
*   **Task:** Connect UI to Backend.
*   **Action:** When user clicks "Submit Answer", trigger the Gemini analysis pipeline and render the returned JSON feedback nicely using `st.markdown` and `st.metric` (for scores).

---

## Phase 3: User Management & Progress (The "App" Feel)
**Objective:** Turn the tool into a personalized platform.

### 3.1 Authentication System
*   **Task:** Build Login Screen.
*   **Action:** Implement a simple credential check against the SQLite User table. Hide the "Exam" content until `st.session_state['authenticated']` is True.
*   **Deliverable:** Secure entry point.

### 3.2 Student Dashboard
*   **Task:** Visualize Progress.
*   **Action:** Create a "Home" tab showing:
    *   History of past sessions.
    *   Average score chart (using `st.line_chart`).
    *   Weakest vocabulary topics.
*   **Deliverable:** A personalized landing page.

---

## Phase 4: Deployment & Polish
**Objective:** Make it stable and "Elegant."

### 4.1 UI Polish
*   **Task:** Theming.
*   **Action:** Configure `.streamlit/config.toml` to match a school or professional color scheme. Remove standard Streamlit menus/footers.

### 4.2 Deployment
*   **Task:** Server Setup.
*   **Action:** Deploy to a secure, private server (e.g., a private VM, internal school server, or Streamlit Community Cloud with password protection).
*   **Deliverable:** A live URL accessible to the closed user group.

---

## Risk Register
*   **Audio Permissions:** Browsers are strict about microphone access. Must ensure the deployment environment (HTTPS) supports audio capture.
*   **Latency:** Streamlit re-runs scripts. Optimization of the "Heavy" AI calls using `@st.cache_data` is critical to prevent re-generating the question every time a button is clicked.
