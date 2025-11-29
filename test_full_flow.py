import os
import sys
import sounddevice as sd
import soundfile as sf
import json
from data_loaders import ThemeLoader, VocabularyLoader
from question_generator import QuestionGenerator
from tts_module import TTSGenerator
from audio_input import AudioRecorder
from analysis_module import ResponseAnalyzer

def play_audio(file_path):
    """Plays an audio file using sounddevice."""
    try:
        data, fs = sf.read(file_path)
        sd.play(data, fs)
        sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}")

def main_test():
    print("Initializing GCSE Language Testing App (Automated Test Mode)...")

    # Initialize modules
    try:
        theme_loader = ThemeLoader("themes.json")
        vocab_loader = VocabularyLoader("vocab.json")
        # Explicitly using gemini-2.5-flash as requested
        question_gen = QuestionGenerator(model_name="gemini-2.5-flash")
        tts_gen = TTSGenerator(model_name="gemini-2.5-flash-preview-tts")
        recorder = AudioRecorder()
        analyzer = ResponseAnalyzer(model_name="gemini-2.5-flash")
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    print("Initialization Complete. Starting Single Exam Question.\n")

    print("-" * 50)
    # 1. Context Selection
    theme, topic, subtopic = theme_loader.get_random_theme_topic_subtopic()
    print(f"Context: {theme} -> {topic} -> {subtopic}")

    # 2. Vocabulary Selection
    vocab_subset = vocab_loader.get_random_words(3)
    
    # 3. Generate Question
    print("Generating question...")
    question_text = question_gen.generate_question(
        theme=theme, 
        topic=topic, 
        subtopic=subtopic, 
        language="Russian",
        vocabulary=vocab_subset
    )
    
    if not question_text:
        print("Failed to generate question.")
        return

    # 4. TTS & Playback
    print("\nExaminer is speaking...")
    audio_file = "current_question.wav"
    if tts_gen.generate_audio(question_text, audio_file, voice_name="Zephyr"):
        play_audio(audio_file)
    else:
        print(f"Examiner (Text only): {question_text}")

    # 5. Student Response (Fixed duration for test)
    response_file = "student_response.wav"
    print("\nSimulating student response (Recording silence/background noise for 5 seconds)...")
    recorder.record_audio_fixed(response_file, duration=5)

    # 6. Analysis
    print("\nAnalyzing response...")
    analysis = analyzer.analyze_response(
        original_question=question_text,
        theme_context=f"{theme} - {topic}",
        audio_file_path=response_file,
        target_language="Russian"
    )

    # 7. Display Results
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

    print("\nTest Session ended.")

if __name__ == "__main__":
    main_test()
