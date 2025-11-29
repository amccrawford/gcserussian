import json
import re

def convert_themes_to_json(md_file_path, json_file_path):
    themes = []
    current_theme = None
    current_topic = None

    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            
            # Match Theme (Level 2 Header)
            if line.startswith("## "):
                # Save previous topic/theme if exists
                if current_topic and current_theme:
                    current_theme["topics"].append(current_topic)
                    current_topic = None
                if current_theme:
                    themes.append(current_theme)
                
                current_theme = {
                    "theme": line.replace("## ", "").strip(),
                    "topics": []
                }
                current_topic = None # Reset topic on new theme

            # Match Topic (Level 3 Header)
            elif line.startswith("### "):
                # Save previous topic if exists
                if current_topic and current_theme:
                    current_theme["topics"].append(current_topic)
                
                current_topic = {
                    "name": line.replace("### ", "").strip(),
                    "subtopics": []
                }

            # Match Subtopic (List item)
            elif line.startswith("- "):
                if current_topic:
                    subtopic = line.replace("- ", "").strip()
                    current_topic["subtopics"].append(subtopic)

        # Append the very last items
        if current_topic and current_theme:
            current_theme["topics"].append(current_topic)
        if current_theme:
            themes.append(current_theme)

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(themes, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully converted '{md_file_path}' to '{json_file_path}'")

    except Exception as e:
        print(f"Error converting themes: {e}")

if __name__ == "__main__":
    convert_themes_to_json("themes.md", "themes.json")
