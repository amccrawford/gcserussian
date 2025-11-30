import os
import random
import json
import tempfile
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Session as DBSession, Result
from auth_utils import verify_password
from data_loaders import ThemeLoader, VocabularyLoader
from question_generator import QuestionGenerator
from tts_module import TTSGenerator
from analysis_module import ResponseAnalyzer
from datetime import datetime

class GameEngine:
    def __init__(self):
        self.theme_loader = ThemeLoader("themes.json")
        self.vocab_loader = VocabularyLoader("vocab.json")
        self.question_gen = QuestionGenerator(model_name="gemini-2.5-flash")
        self.tts_gen = TTSGenerator(model_name="gemini-2.5-flash-preview-tts")
        self.analyzer = ResponseAnalyzer(model_name="gemini-2.5-flash")
        self.available_voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede", "Zephyr"] 

    # --- Authentication & User Management ---
    def login_user(self, username, password):
        """
        Authenticates a user.
        Returns the User object if successful, None otherwise.
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return None
            if not verify_password(password, user.hashed_password):
                return None
            return user
        finally:
            db.close()

    def get_user_stats(self, user_id):
        """
        Retrieves basic statistics for the user dashboard.
        """
        db = SessionLocal()
        try:
            total_sessions = db.query(DBSession).filter(DBSession.user_id == user_id).count()
            
            # Calculate average score
            results = db.query(Result).join(DBSession).filter(DBSession.user_id == user_id).all()
            total_score = sum([r.score for r in results])
            avg_score = round(total_score / len(results), 1) if results else 0
            
            # Recent history
            history = []
            recent_results = db.query(Result).join(DBSession).filter(DBSession.user_id == user_id).order_by(DBSession.timestamp.desc()).limit(5).all()
            for res in recent_results:
                history.append({
                    "date": res.session.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "topic": res.session.topic,
                    "score": res.score
                })

            return {
                "total_sessions": total_sessions,
                "average_score": avg_score,
                "recent_history": history
            }
        finally:
            db.close()

    def save_exam_result(self, user_id, question_data, analysis_result):
        """
        Saves the completed exam interaction to the database.
        """
        if "error" in analysis_result:
            return # Don't save error results

        db = SessionLocal()
        try:
            # 1. Create Session Record
            new_session = DBSession(
                user_id=user_id,
                timestamp=datetime.utcnow(),
                theme=question_data['theme'],
                topic=question_data['topic'],
                subtopic=question_data.get('subtopic'),
                difficulty="easy", # Default for now
                language="Russian"
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)

            # 2. Create Result Record
            new_result = Result(
                session_id=new_session.id,
                original_question=question_data['question_text'],
                question_english_translation=analysis_result.get('original_question_english', ''),
                student_transcription=analysis_result.get('transcription', ''),
                student_translation=analysis_result.get('translation', ''),
                score=int(analysis_result.get('score', 0)),
                feedback_json=analysis_result
            )
            db.add(new_result)
            db.commit()
        except Exception as e:
            print(f"Error saving result to DB: {e}")
            db.rollback()
        finally:
            db.close()

    # --- Core Game Logic ---
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
