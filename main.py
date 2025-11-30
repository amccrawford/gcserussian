import os
import sys
import random
import sounddevice as sd
import soundfile as sf
import json
import time
import tempfile # Added for temporary file cleanup
from services import GameEngine # Import GameEngine
from audio_input import AudioRecorder

# Temporary function for CLI audio playback
def play_audio(file_path):
    """Plays an audio file using sounddevice."""
    try:
        data, fs = sf.read(file_path)
        sd.play(data, fs)
        sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}")

def main():
    print("Initializing GCSE Language Testing App (CLI Version)...")

    # Initialize modules
    try:
        game_engine = GameEngine() # Use the new GameEngine
        recorder = AudioRecorder()
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    print("Initialization Complete. Starting Exam Session.\n")

    while True:
        question_data = None
        student_response_path = None
        try:
            print("-" * 50)
            # 1. Generate Question
            print("Generating question...")
            question_data = game_engine.generate_new_question()
            
            question_text = question_data["question_text"]
            question_audio_path = question_data["question_audio_path"]
            theme = question_data["theme"]
            topic = question_data["topic"]
            examiner_voice = question_data["examiner_voice"]

            print(f"Context: {theme} -> {topic} -> {question_data['subtopic']}")
            print(f"\nExaminer ({examiner_voice}) is speaking...")
            
            # 2. Play TTS audio
            play_audio(question_audio_path)

            # Interaction Menu Loop
            while True:
                print("\nOptions:")
                print("1. Hear question again")
                print("2. See question text")
                print("3. Answer (Record)")
                print("4. Skip this question")
                print("q. Quit")
                
                choice = input("Select an option: ").strip().lower()
                
                if choice == '1':
                    print("\nReplaying audio...")
                    play_audio(question_audio_path)
                elif choice == '2':
                    print(f"\nQuestion: {question_text}")
                elif choice == '3':
                    break
                elif choice == '4':
                    print("Skipping...")
                    break # Breaks inner loop, effectively skipping to next iteration of outer loop
                elif choice == 'q':
                    print("Exiting session.")
                    sys.exit(0)
                else:
                    print("Invalid option. Please try again.")
            
            if choice == '4':
                continue

            # 3. Student Response
            student_response_path = "student_response.wav" # This will be the temporary file
            recorder.record_audio_manual(student_response_path)

            # 4. Analysis
            print("\nAnalyzing your response...")
            theme_context = f"{theme} - {topic}"
            analysis = game_engine.analyze_student_response(
                original_question=question_text,
                theme_context=theme_context,
                student_audio_path=student_response_path,
                target_language="Russian"
            )

            # 5. Display Results
            if "error" in analysis:
                print(f"Analysis Error: {analysis['error']}")
            else:
                print("\n" + "="*20 + " FEEDBACK " + "="*20)
                print(f"Examiner Question (Russian): {question_text}")
                print(f"Examiner Question (English): {analysis.get('original_question_english', 'N/A')}")
                print("-" * 20)
                print(f"Your Response (Transcription): {analysis.get('transcription', 'N/A')}")
                print(f"Your Response (Translation):   {analysis.get('translation', 'N/A')}")
                print("-" * 20)
                print(f"Score: {analysis.get('score', 'N/A')}/10")
                print(f"Feedback: {analysis.get('feedback', 'N/A')}")
                print("="*50)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            # Clean up temporary audio files
            if question_data and "question_audio_path" in question_data and os.path.exists(question_data["question_audio_path"]):
                os.remove(question_data["question_audio_path"])
            if student_response_path and os.path.exists(student_response_path):
                os.remove(student_response_path)
            
            # 6. Loop
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
