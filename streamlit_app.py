import streamlit as st
import os
import tempfile
from services import GameEngine
from streamlit_mic_recorder import mic_recorder # Updated import
import json # For displaying analysis results
from datetime import datetime # For session timestamp

# --- Configuration ---
st.set_page_config(
    page_title="Arabella's GCSE Russian Oral Practice",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Initialize GameEngine (once per session) ---
@st.cache_resource
def get_game_engine():
    return GameEngine()

game_engine = get_game_engine()

# --- Initialize Session State ---
if "current_question_data" not in st.session_state:
    st.session_state.current_question_data = None
if "user_response_audio_bytes" not in st.session_state: # Changed to store bytes directly
    st.session_state.user_response_audio_bytes = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "question_audio_playback_path" not in st.session_state:
    st.session_state.question_audio_playback_path = None

# --- Helper Functions ---
def generate_new_question_ui():
    """Generates a new question and updates session state."""
    with st.spinner("Generating new question..."):
        try:
            question_data = game_engine.generate_new_question()
            st.session_state.current_question_data = question_data
            
            # Save the generated audio to a temp file for Streamlit's st.audio
            if st.session_state.question_audio_playback_path and os.path.exists(st.session_state.question_audio_playback_path):
                try:
                    os.remove(st.session_state.question_audio_playback_path) # Clean up previous audio
                except Exception as e:
                    print(f"Warning: Could not remove previous audio file: {e}")

            # Directly use the path from the service, which is already a temp file
            st.session_state.question_audio_playback_path = question_data["question_audio_path"]
            
            st.session_state.user_response_audio_bytes = None # Clear previous response
            st.session_state.analysis_result = None # Clear previous analysis
            st.toast("New question generated!")
        except Exception as e:
            st.error(f"Error generating question: {e}")
            st.session_state.current_question_data = None
            st.session_state.question_audio_playback_path = None

def analyze_response_ui(audio_bytes):
    """Analyzes the user's audio response."""
    if st.session_state.current_question_data:
        # Save audio_bytes to a temporary file for analysis
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
        except Exception as e:
                st.error(f"Error analyzing response: {e}")
                st.session_state.analysis_result = {"error": str(e)}
        finally:
                if user_audio_filepath and os.path.exists(user_audio_filepath):
                    os.remove(user_audio_filepath) # Clean up user's audio



# --- UI Layout ---
st.title("🗣️ Arabella's GCSE Russian Oral Practice")
st.subheader("Practice your Russian speaking skills!")

# Display current question or generate new one
if st.session_state.current_question_data is None:
    st.button("Start New Exam Session", on_click=generate_new_question_ui, type="primary")
else:
    question_data = st.session_state.current_question_data
    st.markdown(f"**Context:** _{question_data['theme']} -> {question_data['topic']}_")
    st.markdown(f"**Examiner ({question_data['examiner_voice']}) says:**")

    # Audio playback for the question
    if st.session_state.question_audio_playback_path:
        st.audio(st.session_state.question_audio_playback_path, format="audio/wav", start_time=0)
    else:
        st.warning("Question audio not available.")

    # Option to view question text (for help)
    with st.expander("Show Question Text (cheat!)"):
        st.info(question_data["question_text"])

    st.markdown("---")
    st.subheader("Your Response:")

    # Conditionally display recorder or 'Response Recorded' message
    if st.session_state.analysis_result is None:
        # Audio recorder widget
        # Using streamlit_mic_recorder
        audio_output = mic_recorder(start_prompt="Click to Record Your Answer", stop_prompt="Recording...", just_once=False, use_container_width=True, key='mic_recorder')

        if audio_output is not None and "bytes" in audio_output:
            st.session_state.user_response_audio_bytes = audio_output["bytes"]
            if st.session_state.user_response_audio_bytes: # Process only if bytes are actually present
                analyze_response_ui(st.session_state.user_response_audio_bytes)
                st.toast("Response recorded and sent for analysis!")
                st.rerun() # Force rerun to update UI immediately
            else:
                st.warning("No audio recorded.")
    else:
         st.info("Response recorded. See feedback below.")


    # Display Analysis Results
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
        
        # Show 'Get New Question' only after feedback is displayed
        st.button("Get New Question", on_click=generate_new_question_ui)

# --- Cleanup temporary files on shutdown (Streamlit doesn't have a direct shutdown hook) ---
# This is a best-effort cleanup. In a real deployment, a more robust cleanup strategy would be needed.
# For Streamlit, tempfile.NamedTemporaryFile(delete=True) is preferred, but requires writing to memory first.
# Here we manage deletion manually to integrate with existing services.
# A more robust solution for Streamlit would be to handle bytes directly or use st.session_state to store bytes
# and st.audio(data=st.session_state.audio_bytes) without saving to disk.
def cleanup_temp_files():
    if st.session_state.question_audio_playback_path and os.path.exists(st.session_state.question_audio_playback_path):
        os.remove(st.session_state.question_audio_playback_path)
    # The user's response audio is already deleted after analysis

st.sidebar.markdown("This app helps you practice your Russian speaking skills by generating questions and analyzing your responses using Google's Gemini AI.")
