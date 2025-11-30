import os
import random
import json
import tempfile
from data_loaders import ThemeLoader, VocabularyLoader
from question_generator import QuestionGenerator
from tts_module import TTSGenerator
from analysis_module import ResponseAnalyzer

class GameEngine:
    def __init__(self):
        self.theme_loader = ThemeLoader("themes.json")
        self.vocab_loader = VocabularyLoader("vocab.json")
        self.question_gen = QuestionGenerator(model_name="gemini-2.5-flash")
        self.tts_gen = TTSGenerator(model_name="gemini-2.5-flash-preview-tts")
        self.analyzer = ResponseAnalyzer(model_name="gemini-2.5-flash")
        self.available_voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede", "Zephyr"] # Moved from main.py

    def generate_new_question(self):
        """
        Generates a new question, its audio, and returns relevant details.
        Returns a dictionary containing:
            - 'question_text': The generated question text.
            - 'question_audio_path': Path to the generated audio file.
            - 'theme': The selected theme.
            - 'topic': The selected topic.
            - 'subtopic': The selected subtopic.
            - 'vocabulary_used': List of vocabulary used in the question.
            - 'examiner_voice': The voice used for the question.
        """
        try:
            # 1. Context Selection
            theme, topic, subtopic, topic_data = self.theme_loader.get_random_theme_topic_subtopic()

            # 2. Vocabulary Selection
            vocab_subset = self.vocab_loader.get_contextual_words(
                theme, topic, subtopic, topic_data=topic_data, count=5
            )

            # 3. Generate Question Text
            question_text = self.question_gen.generate_question(
                theme=theme, 
                topic=topic, 
                subtopic=subtopic, 
                language="Russian",
                vocabulary=vocab_subset,
                difficulty_level="easy" # Default to easy for now
            )
            if not question_text:
                raise RuntimeError("Failed to generate question text.")

            # 4. TTS for Question
            selected_voice = random.choice(self.available_voices)
            
            # Create a temporary file for the audio
            # The Streamlit app will need to manage these temporary files
            temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_audio_file.close() # Close to allow writing by tts_gen

            audio_bytes = self.tts_gen.generate_audio(question_text, voice_name=selected_voice)
            with open(temp_audio_file.name, "wb") as f:
                f.write(audio_bytes)
            
            return {
                "question_text": question_text,
                "question_audio_path": temp_audio_file.name,
                "theme": theme,
                "topic": topic,
                "subtopic": subtopic,
                "vocabulary_used": [v['russian'] for v in vocab_subset],
                "examiner_voice": selected_voice
            }
        except Exception as e:
            raise RuntimeError(f"Error generating new question: {e}")

    def analyze_student_response(self, original_question, theme_context, student_audio_path, target_language="Russian"):
        """
        Analyzes the student's audio response.
        """
        try:
            analysis = self.analyzer.analyze_response(
                original_question=original_question,
                theme_context=theme_context,
                audio_file_path=student_audio_path,
                target_language=target_language
            )
            return analysis
        except Exception as e:
            raise RuntimeError(f"Error analyzing student response: {e}")
