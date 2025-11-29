from syllabus_parser import SyllabusParser
import os

def test_parser(syllabus_file_path="syllabus.md"):
    print(f"Testing SyllabusParser with '{syllabus_file_path}'...")
    
    if not os.path.exists(syllabus_file_path):
        print(f"Error: Syllabus file '{syllabus_file_path}' not found. Please ensure it exists.")
        return

    parser = SyllabusParser(syllabus_file_path)
    
    sections = parser.get_sections()

    if sections:
        print("\n--- Parsed Syllabus Sections (Titles) ---")
        for title in sections.keys():
            print(f"- {title}")
        
        print("\n--- Testing Random Topic Retrieval ---")
        topic_title, topic_content = parser.get_random_topic()
        if topic_title and topic_content:
            print(f"Random Topic: {topic_title}")
            print(f"Content snippet (first 300 chars):\n{topic_content[:300]}...")
        else:
            print("Could not retrieve a random topic.")
            
        print("\n--- Testing Specific Topic Retrieval (e.g., 'Themes and topics') ---")
        specific_topic_content = parser.get_topic_by_title("Themes and topics")
        if specific_topic_content:
            print(f"Themes and topics content snippet (first 300 chars):\n{specific_topic_content[:300]}...")
        else:
            print("Specific topic 'Themes and topics' not found.")
    else:
        print("Syllabus parsing failed or no sections were found.")

if __name__ == "__main__":
    test_parser()
