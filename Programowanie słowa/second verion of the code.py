import nltk
from nltk.corpus import inaugural
from nltk.tokenize import word_tokenize
from collections import Counter
import os

# Ensure necessary NLTK resources are downloaded
nltk.download('inaugural')
nltk.download('punkt')

# Define window sizes and output directory
window_sizes = range(1, 11)  # Window sizes from 1 to 10
output_directory = "C:/Users/Tymon/Documents/Programowanie_słowa/"
os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

def get_nouns_from_text(text):
    """
    Tokenizes the text and filters for nouns.
    """
    tokens = word_tokenize(text)
    # Placeholder for POS tagging (Inaugural corpus does not have POS tags)
    # Example: Use a dummy POS tagging if actual POS tagging is not available
    tagged_tokens = nltk.pos_tag(tokens)
    nouns_list = [word.lower() for word, tag in tagged_tokens if tag.startswith('NN')]
    return nouns_list

for window_size in window_sizes:
    output_file_path = f"{output_directory}output_window_{window_size}.txt"
    with open(output_file_path, "w", encoding="utf-8") as file:
        print(f"Processing window size {window_size}...", file=file)
        
        # Build the nouns list from Inaugural corpus
        print("Building nouns list from Inaugural corpus...", file=file)
        singular_noun_counter = Counter()
        sentences = inaugural.sents()
        nouns_list = []
        for sentence in sentences:
            text = ' '.join(sentence)  # Join tokens to form a single string
            nouns_list.extend(get_nouns_from_text(text))
        
        # Define your functions here (e.g., `most_unique_occurrences`)
        def most_unique_occurrences(nouns_list, window_size=10):
            unique_counts = {}
            word_neighbors = {}
            
            for i, word in enumerate(nouns_list):
                surroundings = tuple(nouns_list[max(0, i - window_size): i] + nouns_list[i + 1: min(len(nouns_list), i + window_size + 1)])
                if word not in unique_counts:
                    unique_counts[word] = set()
                unique_counts[word].add(surroundings)
                
                if word not in word_neighbors:
                    word_neighbors[word] = set()
                
                for j in range(-window_size, window_size + 1):
                    if i + j >= 0 and i + j < len(nouns_list) and j != 0:
                        word_neighbors[word].add(nouns_list[i + j])
            
            words_with_unique_counts = [(word, len(unique_counts[word]), list(word_neighbors[word])) for word in unique_counts]
            sorted_words = sorted(words_with_unique_counts, key=lambda x: x[1], reverse=True)
            return sorted_words
        
        # Process and save results
        filtered_unique_words = most_unique_occurrences(nouns_list, window_size)
        for word, uniqueness_value, neighbors in filtered_unique_words:
            print(f"Word: {word}, Uniqueness Value: {uniqueness_value}", file=file)
        
        print(f"Finished writing results for window size {window_size} to {output_file_path}.", file=file)

print("All window sizes processed.")
