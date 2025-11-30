import os
import sys
import random
import sounddevice as sd
import soundfile as sf
import json
import time
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

def main():
    print("Initializing GCSE Language Testing App (CLI Version)...")

    # Initialize modules
    try:
        theme_loader = ThemeLoader("themes.json")
        vocab_loader = VocabularyLoader("vocab.json")
        question_gen = QuestionGenerator(model_name="gemini-2.5-flash")
        tts_gen = TTSGenerator(model_name="gemini-2.5-flash-preview-tts")
        recorder = AudioRecorder()
        analyzer = ResponseAnalyzer(model_name="gemini-2.5-flash")
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    print("Initialization Complete. Starting Exam Session.\n")

    while True:
        print("-" * 50)
        # 1. Context Selection
        theme, topic, subtopic, topic_data = theme_loader.get_random_theme_topic_subtopic()
        print(f"Context: {theme} -> {topic} -> {subtopic}")

        # 2. Vocabulary Selection
        vocab_subset = vocab_loader.get_contextual_words(
            theme, topic, subtopic, topic_data=topic_data, count=5
        )
        # print(f"Target Vocabulary: {[v['russian'] for v in vocab_subset]}") 

        # 3. Generate Question
        print("Generating question...")
        try:
            question_text = question_gen.generate_question(
                theme=theme, 
                topic=topic, 
                subtopic=subtopic, 
                language="Russian",
                vocabulary=vocab_subset,
                difficulty_level="easy" # Default to easy for now
            )
        except Exception as e:
            print(f"Error generating question: {e}")
            continue
        
        if not question_text:
            print("Failed to generate question. Retrying...")
            continue

        # 4. TTS & Playback
        voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede", "Zephyr"]
        selected_voice = random.choice(voices)
        print(f"\nExaminer ({selected_voice}) is speaking...")
        audio_file = "current_question.wav"
        
        try:
            audio_bytes = tts_gen.generate_audio(question_text, voice_name=selected_voice)
            with open(audio_file, "wb") as f:
                f.write(audio_bytes)
            play_audio(audio_file)
        except Exception as e:
            print(f"TTS Error: {e}")
            print(f"Examiner (Text only): {question_text}")

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
                play_audio(audio_file)
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

        # 5. Student Response
        response_file = "student_response.wav"
        recorder.record_audio_manual(response_file)

        # 6. Analysis
        print("\nAnalyzing your response...")
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

        # 8. Loop
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
