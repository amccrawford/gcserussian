import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QuestionGenerator:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_question(self, theme, topic, subtopic=None, language="Russian", vocabulary=None):
        """
        Generates a GCSE-style oral exam question based on the provided context. 
        
        Args:
            theme (str): The broader theme.
            topic (str): The specific topic.
            subtopic (str, optional): A more specific subtopic.
            language (str): Target language (default: Russian).
            vocabulary (list, optional): A list of vocabulary words to potentially include.

        Returns:
            str: The generated question in the target language.
        """
        
        context_str = f"Theme: {theme}\nTopic: {topic}"
        if subtopic:
            context_str += f"\nSubtopic: {subtopic}"
        
        vocab_instruction = ""
        if vocabulary:
            vocab_list_str = ", ".join([v['russian'] for v in vocabulary])
            vocab_instruction = f"Try to incorporate one or more of the following words/phrases naturally if possible: {vocab_list_str}."

        difficulty_level = "easy"  # Can be adjusted or made dynamic if needed
        
        prompt = f"""
        You are a GCSE {language} examiner conducting a speaking exam.
        
        Generate a SINGLE, clear, and open-ended oral exam question suitable for a student (approx. 15-16 years old).
        
        Context:
        {context_str}
        
        {vocab_instruction}
        
        Requirements:
        1. The question MUST be in {language}.
        2. The question should be clear and short - preferably no more than one sentence.
        3. The question should encourage the student to express opinions or describe events (past, present, or future).
        4. On a scale of easy-medium-hard, aim for a question that is {difficulty_level}.
        5. Do not provide the English translation.
        6. Do not provide any introductory text or preamble. Output ONLY the question.
        7. Keep the language level appropriate for GCSE Foundation/Higher tier.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating question: {e}")
            return None

if __name__ == "__main__":
    # Test the generator
    try:
        generator = QuestionGenerator()
        
        # Dummy data for test
        test_theme = "Theme 1: Identity and culture"
        test_topic = "Daily life"
        test_subtopic = "food and drink"
        test_vocab = [{'english': 'apple', 'russian': 'яблоко'}, {'english': 'breakfast', 'russian': 'завтрак'}]
        
        print("Generating test question...")
        question = generator.generate_question(test_theme, test_topic, test_subtopic, vocabulary=test_vocab)
        
        if question:
            print(f"\nGenerated Question (Russian): {question}")
        else:
            print("Failed to generate question.")
            
    except ValueError as e:
        print(f"Setup Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
