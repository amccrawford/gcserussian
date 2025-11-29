# Development Workplan: GCSE Language Testing App

This document outlines the step-by-step development plan for a Python-based GCSE language testing application. The application will utilize Generative AI for content creation, audio synthesis, and student assessment.

## Phase 1: Project Setup and Architecture

### 1.1. Environment Initialization
*   **Objective:** Set up a clean development environment.
*   **Actions:**
    *   Initialize a Git repository.
    *   Create a Python virtual environment.
    *   Create a `requirements.txt` file (to be populated as libraries are chosen).
    *   Set up a `.env` file for securely storing API keys (e.g., Google Gemini API key).

### 1.2. Library Selection
*   **Objective:** Identify necessary Python packages.
*   **Requirements:**
    *   **LLM & Multimodal Interaction:** `google-generativeai` (for Gemini).
    *   **Audio Recording:** `pyaudio` or `sounddevice`.
    *   **Audio Playback:** `playsound`, `pydub`, or `pygame`.
    *   **System Operations:** `os`, `dotenv`, `time`, `json`.

## Phase 2: Data Loading Module

### 2.1. Theme Loader
*   **Objective:** Ingest the structured curriculum topics.
*   **Logic:**
    *   Create a function to read `themes.json`.
    *   Implement logic to randomly select a Theme, Topic, and Subtopic for the current session context.

### 2.2. Vocabulary Loader
*   **Objective:** Ingest the expected vocabulary.
*   **Logic:**
    *   Create a function to read `vocab.json`.
    *   Implement logic to filter or select vocabulary relevant to the chosen theme (if categorized) or provide a random selection of "expected words" to guide the generation.

## Phase 3: Question Generation Module

### 3.1. Prompt Engineering (Generation)
*   **Objective:** Instruct the LLM to function as a GCSE examiner.
*   **Logic:**
    *   Design a system prompt that defines the persona (GCSE Examiner).
    *   Construct a dynamic prompt that accepts:
        *   **Context:** The selected Theme/Topic from `themes.json`.
        *   **Vocabulary:** A subset of relevant words from `vocab.json` that the question should aim to elicit or utilise.
        *   **Language:** Target language (French/Russian).
    *   **Constraint:** The output must be a single, clear question suitable for a GCSE oral exam.

### 3.2. Generation Function
*   **Objective:** Get the text question from the API.
*   **Logic:**
    *   Call the Gemini API with the prompt.
    *   Extract and sanitize the text response.

## Phase 4: Audio Output (TTS) Module

### 4.1. TTS Integration
*   **Objective:** Convert the generated text question into spoken audio.
*   **Logic:**
    *   Utilize the Gemini API's text-to-speech capabilities (or a dedicated Google Cloud TTS integration if Gemini direct TTS is not being used).
    *   Request the audio in the specific target language voice (French/Russian).

### 4.2. Audio Playback
*   **Objective:** Play the question to the student.
*   **Logic:**
    *   Save the received audio stream to a temporary file (e.g., `question.mp3`).
    *   Use an audio library to play the file to the user.

## Phase 5: Student Response Module (Audio Input)

### 5.1. Recording Logic
*   **Objective:** Capture the student's answer.
*   **Logic:**
    *   Implement a "Press Enter to Start/Stop Recording" or a silence-detection mechanism.
    *   Capture microphone input using the chosen audio library.
    *   Save the input as a temporary audio file (e.g., `response.wav` or `response.mp3`).

## Phase 6: Analysis and Evaluation Module

### 6.1. Multimodal Analysis (The "Brain")
*   **Objective:** Transcribe, translate, and grade the response in one pass (leveraging Gemini's multimodal audio capabilities).
*   **Logic:**
    *   Construct a complex prompt that includes:
        1.  The original text question.
        2.  The Theme/Topic context.
        3.  The student's audio file (uploaded/attached to the prompt).
    *   **Instructions to LLM:**
        *   Transcribe the audio to text (in the target language).
        *   Translate the response to English.
        *   Translate the *original question* to English.
        *   Evaluate the grammar, pronunciation, and relevance (Score 1-10).
        *   Provide specific constructive feedback.

### 6.2. Response Parsing
*   **Objective:** specific structured data from the LLM response.
*   **Logic:**
    *   Request the output in a structured format (like JSON) or parse the text to separate the sections (Transcription, Translation, Score, Feedback).

## Phase 7: User Interface and Integration

### 7.1. Main Application Loop
*   **Objective:** Tie all modules together into a workflow.
*   **Flow:**
    1.  Load Themes and Vocabulary.
    2.  Select random Theme/Topic.
    3.  Generate Question (Text) using Theme + Vocab context.
    4.  Generate Audio (TTS) & Play.
    5.  Record User Response.
    6.  Send Audio + Context to LLM for Analysis.
    7.  Print formatted Analysis to console.
    8.  Ask if the user wants another question.

### 7.2. Display Formatting
*   **Objective:** Make the text output readable.
*   **Logic:**
    *   Use clear headings and spacing in the console output to separate the "Examiner Question," "Translation," and "Feedback."

## Phase 8: Testing and Refinement

*   **Latency Check:** Measure the time between user finishing speaking and receiving feedback. Optimize prompt length if necessary.
*   **Audio Levels:** Ensure recording volume is sufficient for the AI to understand.
*   **Edge Cases:** Handle API timeouts, microphone errors, or empty audio files.