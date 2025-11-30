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
        Returns (theme_name, topic_name, subtopic_name) and the topic object itself (which contains vocab_categories).
        """
        if not self.themes_data:
            return None, None, None, None

        random_theme = random.choice(self.themes_data)
        theme_name = random_theme["theme"]

        if not random_theme["topics"]:
            return theme_name, None, None, None
        
        random_topic = random.choice(random_theme["topics"])
        topic_name = random_topic["name"]

        if random_topic.get("subtopics"):
            random_subtopic = random.choice(random_topic["subtopics"])
            return theme_name, topic_name, random_subtopic, random_topic
        else:
            return theme_name, topic_name, None, random_topic

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

    def get_contextual_words(self, theme, topic, subtopic, topic_data=None, count=5):
        """
        Returns a list of vocabulary words relevant to the context.
        Uses hierarchical filtering: 
        1. Subtopic match (keyword)
        2. Mapped Categories (from themes.json)
        3. Fallback to general vocabulary.
        """
        relevant_words = []
        
        # 1. Collect categories from the topic data (mapped in Phase 1)
        mapped_categories = []
        if topic_data and "vocab_categories" in topic_data:
            mapped_categories = topic_data["vocab_categories"]
        
        # 2. Filter vocabulary based on mapped categories
        if mapped_categories:
            for word in self.vocab_data:
                if word["category"] in mapped_categories:
                    relevant_words.append(word)
        
        # 3. Optional: Keyword matching for subtopic (simple containment)
        # if subtopic:
        #     subtopic_keywords = subtopic.lower().split()
        #     for word in self.vocab_data:
        #         # Avoid duplicates
        #         if word not in relevant_words: 
        #             if any(k in word['category'].lower() or k in word['english'].lower() for k in subtopic_keywords):
        #                 relevant_words.append(word)

        # 4. Fill quota if we don't have enough words
        if len(relevant_words) < count:
            # Fetch some general high-frequency words to pad the list
            general_cats = ["Common verbs", "Common adjectives", "Time expressions", "Other high-frequency words"]
            general_pool = [w for w in self.vocab_data if w["category"] in general_cats]
            
            needed = count - len(relevant_words)
            # Add random general words
            if general_pool:
                relevant_words.extend(random.sample(general_pool, min(needed, len(general_pool))))
        
        # 5. Final Selection
        if not relevant_words:
            # Absolute fallback if everything fails
            return self.get_random_words(count)
            
        # Shuffle and return unique count
        # Ensure uniqueness (dictionaries are not hashable, so use index or tuple)
        unique_words = {v['english']:v for v in relevant_words}.values()
        final_pool = list(unique_words)
        
        return random.sample(final_pool, min(count, len(final_pool)))

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
                {"name": "Who am I?", "subtopics": ["relationships", "when I was younger"], "vocab_categories": ["greeting", "relationships"]},
                {"name": "Daily life: customs and everyday life", "subtopics": ["food and drink", "shopping"], "vocab_categories": ["food"]}
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
            {"english": "friend", "russian": "друг", "category": "relationships"},
            {"english": "go", "russian": "идти", "category": "Common verbs"}
        ]
        with open(vocab_json_path, 'w', encoding='utf-8') as f:
            json.dump(dummy_vocab, f, indent=4, ensure_ascii=False)

    print("--- Testing ThemeLoader ---")
    try:
        theme_loader = ThemeLoader(themes_json_path)
        print("Themes loaded successfully.")
        
        theme, topic, subtopic, topic_data = theme_loader.get_random_theme_topic_subtopic()
        print(f"\nRandomly selected context:")
        print(f"  Theme: {theme}")
        print(f"  Topic: {topic}")
        print(f"  Subtopic: {subtopic}")
        print(f"  Topic Data (Categories): {topic_data.get('vocab_categories', [])}")

    except Exception as e:
        print(f"Error testing ThemeLoader: {e}")

    print("\n--- Testing VocabularyLoader ---")
    try:
        vocab_loader = VocabularyLoader(vocab_json_path)
        print("Vocabulary loaded successfully.")
        
        print("\nTesting Contextual Selection:")
        context_words = vocab_loader.get_contextual_words(theme, topic, subtopic, topic_data, count=5)
        print(f"Contextual Words: {context_words}")

    except Exception as e:
        print(f"Error testing VocabularyLoader: {e}")