import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class ResponseAnalyzer:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def analyze_response(self, original_question, theme_context, audio_file_path, target_language="Russian"):
        """
        Analyzes the student's audio response using Gemini's multimodal capabilities.
        """
        if not os.path.exists(audio_file_path):
            return {"error": "Audio file not found."}

        # Read audio file bytes
        try:
            with open(audio_file_path, "rb") as f:
                audio_bytes = f.read()
        except Exception as e:
            return {"error": f"Failed to read audio file: {e}"}

        prompt = f"""
        You are an expert GCSE {target_language} examiner. You have just asked a student the following question:
        
        Original Question: "{original_question}"
        Context: {theme_context}
        
        The student has responded in the attached audio file.
        
        Please perform the following analysis and output the result in strictly valid JSON format with the following keys:
        
        1.  "original_question_english": Translate the original question into English.
        2.  "transcription": Transcribe the student's audio response exactly as spoken in {target_language}. If it is not spoken in 
        {target_language}, transcribe it in the language spoken.
        3.  "translation": Translate the student's response into English.
        4.  "score": A score out of 10 (integer) based on GCSE speaking criteria (Communication, Accuracy, Pronunciation).
        5.  "feedback": A concise paragraph giving constructive feedback. Mention what was good and what could be improved (grammar, vocabulary, pronunciation).
        
        JSON Output:
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                            types.Part.from_bytes(
                                data=audio_bytes,
                                mime_type="audio/wav"
                            )
                        ]
                    )
                ]
            )
            
            response_text = response.text.strip()
            
            # Clean up potential markdown formatting (```json ... ```)
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()
                
            return json.loads(response_text)

        except json.JSONDecodeError:
            return {"error": "JSON parsing failed", "raw_text": response_text}
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}

if __name__ == "__main__":
    # Test the analyzer
    analyzer = ResponseAnalyzer()
    
    # Use dummy data for the test
    test_question = "Расскажи о своём типичном завтраке."
    test_context = "Theme: Identity and culture"
    test_audio = "user_response.wav" # Ensure this file exists from the previous step
    
    if os.path.exists(test_audio):
        print("Analyzing response...")
        analysis = analyzer.analyze_response(test_question, test_context, test_audio)
        print(json.dumps(analysis, indent=4, ensure_ascii=False))
    else:
        print(f"Test audio file '{test_audio}' not found. Please run Phase 5 test first.")
