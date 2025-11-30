import streamlit as st
import os
import tempfile
from services import GameEngine
from streamlit_mic_recorder import mic_recorder
import json
from datetime import datetime

# --- Configuration ---
st.set_page_config(
    page_title="Arabella's GCSE Russian Oral Practice",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS for Polish ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            margin-top: -80px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Initialize GameEngine (once per session) ---
@st.cache_resource
def get_game_engine():
    return GameEngine()

game_engine = get_game_engine()

# --- Initialize Session State ---
if "user" not in st.session_state:
    st.session_state.user = None
if "current_question_data" not in st.session_state:
    st.session_state.current_question_data = None
if "user_response_audio_bytes" not in st.session_state:
    st.session_state.user_response_audio_bytes = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "question_audio_playback_path" not in st.session_state:
    st.session_state.question_audio_playback_path = None

# --- Helper Functions ---
def login():
    username = st.session_state.username_input
    password = st.session_state.password_input
    user = game_engine.login_user(username, password)
    if user:
        st.session_state.user = user
        st.session_state.page = "dashboard"
    else:
        st.error("Invalid username or password")

def logout():
    st.session_state.user = None
    st.session_state.page = "login"
    st.session_state.current_question_data = None
    st.session_state.analysis_result = None

def generate_new_question_ui():
    """Generates a new question and updates session state."""
    with st.spinner("Generating new question..."):
        try:
            question_data = game_engine.generate_new_question()
            st.session_state.current_question_data = question_data
            
            # Save the generated audio to a temp file for Streamlit's st.audio
            if st.session_state.question_audio_playback_path and os.path.exists(st.session_state.question_audio_playback_path):
                try:
                    os.remove(st.session_state.question_audio_playback_path)
                except Exception as e:
                    print(f"Warning: Could not remove previous audio file: {e}")

            st.session_state.question_audio_playback_path = question_data["question_audio_path"]
            st.session_state.user_response_audio_bytes = None
            st.session_state.analysis_result = None
            st.toast("New question generated!")
        except Exception as e:
            st.error(f"Error generating question: {e}")
            st.session_state.current_question_data = None
            st.session_state.question_audio_playback_path = None

def analyze_response_ui(audio_bytes):
    """Analyzes the user's audio response and saves the result."""
    if st.session_state.current_question_data and st.session_state.user:
        user_audio_filepath = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
                temp_audio_file.write(audio_bytes)
                user_audio_filepath = temp_audio_file.name

            with st.spinner("Analyzing your response..."):
                question_text = st.session_state.current_question_data["question_text"]
                theme_context = f"{st.session_state.current_question_data['theme']} - {st.session_state.current_question_data['topic']}"
                
                analysis = game_engine.analyze_student_response(
                    original_question=question_text,
                    theme_context=theme_context,
                    student_audio_path=user_audio_filepath
                )
                st.session_state.analysis_result = analysis
                
                # Save result to DB
                game_engine.save_exam_result(
                    user_id=st.session_state.user.id,
                    question_data=st.session_state.current_question_data,
                    analysis_result=analysis
                )

        except Exception as e:
                st.error(f"Error analyzing response: {e}")
                st.session_state.analysis_result = {"error": str(e)}
        finally:
                if user_audio_filepath and os.path.exists(user_audio_filepath):
                    os.remove(user_audio_filepath)

# --- Pages ---

def login_page():
    st.title("🔐 Login")
    with st.form("login_form"):
        st.text_input("Username", key="username_input")
        st.text_input("Password", type="password", key="password_input")
        st.form_submit_button("Login", on_click=login)

def dashboard_page():
    st.title(f"👋 Welcome, {st.session_state.user.username}!")
    
    stats = game_engine.get_user_stats(st.session_state.user.id)
    
    col1, col2 = st.columns(2)
    col1.metric("Total Sessions", stats["total_sessions"])
    col2.metric("Average Score", f"{stats['average_score']}/10")
    
    st.subheader("Recent History")
    if stats["recent_history"]:
        for item in stats["recent_history"]:
            st.text(f"{item['date']} - {item['topic']} (Score: {item['score']})")
    else:
        st.info("No history yet.")
        
    st.markdown("---")
    if st.button("Start Practice Session", type="primary"):
        st.session_state.page = "exam"
        st.rerun()

def exam_page():
    st.title("🗣️ Practice Session")
    
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    # Exam Logic
    if st.session_state.current_question_data is None:
        st.info("Click below to start.")
        st.button("Start New Question", on_click=generate_new_question_ui, type="primary")
    else:
        question_data = st.session_state.current_question_data
        st.markdown(f"**Context:** _{question_data['theme']} -> {question_data['topic']}_")
        st.markdown(f"**Examiner ({question_data['examiner_voice']}) says:**")

        if st.session_state.question_audio_playback_path:
            st.audio(st.session_state.question_audio_playback_path, format="audio/wav", start_time=0)
        else:
            st.warning("Question audio not available.")

        with st.expander("Show Question Text (cheat!)"):
            st.info(question_data["question_text"])

        st.markdown("---")
        st.subheader("Your Response:")

        if st.session_state.analysis_result is None:
            audio_output = mic_recorder(start_prompt="Click to Record", stop_prompt="Recording...", just_once=False, use_container_width=True, key='mic_recorder')
            if audio_output is not None and "bytes" in audio_output:
                st.session_state.user_response_audio_bytes = audio_output["bytes"]
                if st.session_state.user_response_audio_bytes:
                    analyze_response_ui(st.session_state.user_response_audio_bytes)
                    st.toast("Response recorded!")
                    st.rerun()
        else:
             st.info("Response recorded. See feedback below.")

        if st.session_state.analysis_result:
            st.markdown("---")
            st.subheader("Feedback:")
            analysis = st.session_state.analysis_result
            if "error" in analysis:
                st.error(f"Analysis Error: {analysis['error']}")
            else:
                st.metric("Score", f"{analysis.get('score', 'N/A')}/10")
                st.write(f"**Original Question (English):** {analysis.get('original_question_english', 'N/A')}")
                st.write(f"**Your Response (Transcription):** {analysis.get('transcription', 'N/A')}")
                st.write(f"**Your Response (Translation):** {analysis.get('translation', 'N/A')}")
                st.success(f"**Feedback:** {analysis.get('feedback', 'N/A')}")
            
            st.button("Get New Question", on_click=generate_new_question_ui)

# --- Main Router ---
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.user is None:
    login_page()
else:
    with st.sidebar:
        st.write(f"User: {st.session_state.user.username}")
        st.button("Logout", on_click=logout)
    
    if st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "exam":
        exam_page()
