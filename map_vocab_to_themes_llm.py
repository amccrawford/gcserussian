import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def map_vocab_using_llm():
    # 1. Setup Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # 2. Load Data
    try:
        with open("vocab_categories.txt", "r", encoding="utf-8") as f:
            vocab_cats = [line.strip() for line in f.readlines() if line.strip()]
        
        with open("themes.json", "r", encoding="utf-8") as f:
            themes_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    vocab_cats_str = "\n".join(vocab_cats)

    # 3. Iterate and Query LLM
    print("Starting LLM mapping process...")
    
    for theme in themes_data:
        theme_name = theme["theme"]
        for topic in theme["topics"]:
            topic_name = topic["name"]
            subtopics = ", ".join(topic["subtopics"])
            
            print(f"Processing Topic: {topic_name}...")

            prompt = f"""
            You are assisting in mapping a language syllabus to a vocabulary list.
            
            SYLLABUS CONTEXT:
            Theme: {theme_name}
            Topic: {topic_name}
            Subtopics: {subtopics}

            AVAILABLE VOCABULARY CATEGORIES:
            {vocab_cats_str}

            TASK:
            Identify the 3 to 6 most relevant \"Vocabulary Categories\" from the list above that would contain words useful for discussing this specific Topic.
            Include specific categories (like \"Food and drink\") AND relevant general categories (like \"Common verbs\" or \"Time expressions\") if strictly applicable.
            
            OUTPUT FORMAT:
            Return ONLY the exact names of the categories chosen from the list, separated by a pipe character (|). 
            Example: Common verbs|Food and drink|Time expressions
            Do not include any other text.
            """

            try:
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Parse response
                selected_cats = [cat.strip() for cat in response_text.split('|')]
                
                # Validate categories (simple check)
                valid_cats = [cat for cat in selected_cats if cat in vocab_cats]
                
                # Fallback if LLM halluncinated slightly or formatting was off, 
                # try to fuzzy match or just keep valid ones. 
                # For now, strictly keeping valid ones to ensure code safety.
                if len(valid_cats) < len(selected_cats):
                    print(f"  Warning: Some returned categories were invalid/hallucinated and removed: {set(selected_cats) - set(valid_cats)}")

                topic["vocab_categories"] = valid_cats
                print(f"  Mapped: {valid_cats}")
                
                # Rate limit safety
                time.sleep(1) 

            except Exception as e:
                print(f"  Error processing topic '{topic_name}': {e}")
                topic["vocab_categories"] = []

    # 4. Save Result
    try:
        with open("themes.json", "w", encoding="utf-8") as f:
            json.dump(themes_data, f, indent=4, ensure_ascii=False)
        print("Success! themes.json has been updated with LLM-derived vocabulary mappings.")
    except Exception as e:
        print(f"Error saving themes.json: {e}")

if __name__ == "__main__":
    map_vocab_using_llm()
