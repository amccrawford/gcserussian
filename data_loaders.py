import json
import random
import os

class ThemeLoader:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.themes_data = self._load_data()

    def _load_data(self):
        """Loads theme data from the specified JSON file."""
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"Theme JSON file not found at: {self.json_file_path}")
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from '{self.json_file_path}': {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred loading theme data: {e}")

    def get_all_themes(self):
        """Returns all loaded themes data."""
        return self.themes_data

    def get_random_theme_topic_subtopic(self):
        """
        Selects a random theme, a random topic within that theme,
        and a random subtopic (if available), returning them as a tuple.
        Returns (theme_name, topic_name, subtopic_name) or (theme_name, topic_name, None).
        """
        if not self.themes_data:
            return None, None, None

        random_theme = random.choice(self.themes_data)
        theme_name = random_theme["theme"]

        if not random_theme["topics"]:
            return theme_name, None, None
        
        random_topic = random.choice(random_theme["topics"])
        topic_name = random_topic["name"]

        if random_topic["subtopics"]:
            random_subtopic = random.choice(random_topic["subtopics"])
            return theme_name, topic_name, random_subtopic
        else:
            return theme_name, topic_name, None

class VocabularyLoader:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.vocab_data = self._load_data()

    def _load_data(self):
        """Loads vocabulary data from the specified JSON file."""
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"Vocabulary JSON file not found at: {self.json_file_path}")
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from '{self.json_file_path}': {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred loading vocabulary data: {e}")

    def get_all_vocabulary(self):
        """Returns all loaded vocabulary data."""
        return self.vocab_data

    def get_vocabulary_by_category(self, category):
        """Filters vocabulary by category."""
        return [word for word in self.vocab_data if word["category"].lower() == category.lower()]

    def get_random_words(self, count, category=None):
        """
        Returns a specified number of random words from the vocabulary.
        Can optionally filter by category.
        """
        source_vocab = self.vocab_data
        if category:
            source_vocab = self.get_vocabulary_by_category(category)

        if not source_vocab:
            return []
        
        return random.sample(source_vocab, min(count, len(source_vocab)))

if __name__ == "__main__":
    # Ensure themes.json and vocab.json exist for testing
    themes_json_path = "themes.json"
    vocab_json_path = "vocab.json"

    # Dummy themes.json for testing if it doesn't exist
    if not os.path.exists(themes_json_path):
        print(f"Creating a dummy '{themes_json_path}' for testing.")
        dummy_themes = [
            {"theme": "Theme 1: Identity and culture", "topics": [
                {"name": "Who am I?", "subtopics": ["relationships", "when I was younger"]},
                {"name": "Daily life: customs and everyday life", "subtopics": ["food and drink", "shopping"]}
            ]},
            {"theme": "Theme 2: Local area, holiday and travel", "topics": [
                {"name": "Holidays: preferences", "subtopics": ["experiences", "destinations"]},
                {"name": "Travel and tourist transactions: travel and accommodation", "subtopics": []}
            ]}
        ]
        with open(themes_json_path, 'w', encoding='utf-8') as f:
            json.dump(dummy_themes, f, indent=4, ensure_ascii=False)

    # Dummy vocab.json for testing if it doesn't exist
    if not os.path.exists(vocab_json_path):
        print(f"Creating a dummy '{vocab_json_path}' for testing.")
        dummy_vocab = [
            {"english": "hello", "russian": "привет", "category": "greeting"},
            {"english": "cat", "russian": "кошка", "category": "animal"},
            {"english": "dog", "russian": "собака", "category": "animal"},
            {"english": "apple", "russian": "яблоко", "category": "food"},
            {"english": "travel", "russian": "путешествие", "category": "travel"},
            {"english": "friend", "russian": "друг", "category": "relationships"}
        ]
        with open(vocab_json_path, 'w', encoding='utf-8') as f:
            json.dump(dummy_vocab, f, indent=4, ensure_ascii=False)

    print("--- Testing ThemeLoader ---")
    try:
        theme_loader = ThemeLoader(themes_json_path)
        print("Themes loaded successfully.")
        
        theme, topic, subtopic = theme_loader.get_random_theme_topic_subtopic()
        print(f"\nRandomly selected context:")
        print(f"  Theme: {theme}")
        print(f"  Topic: {topic}")
        print(f"  Subtopic: {subtopic}")

    except Exception as e:
        print(f"Error testing ThemeLoader: {e}")

    print("\n--- Testing VocabularyLoader ---")
    try:
        vocab_loader = VocabularyLoader(vocab_json_path)
        print("Vocabulary loaded successfully.")
        
        random_words = vocab_loader.get_random_words(3)
        print(f"\nRandomly selected 3 words: {random_words}")

        animal_words = vocab_loader.get_vocabulary_by_category("animal")
        print(f"\nWords in 'animal' category: {animal_words}")

    except Exception as e:
        print(f"Error testing VocabularyLoader: {e}")
