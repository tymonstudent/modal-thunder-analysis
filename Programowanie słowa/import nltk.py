import nltk
from nltk.corpus import brown
from collections import Counter
import sys

nltk.download("brown")

window_size=10
output_file_path = "C:/Users/Tymon/Documents/Programowanie słowa/output.txt"

# Open the file for writing
with open(output_file_path, "w") as file:
    sys.stdout = file

    # Counting singular nouns in a subset of the Brown Corpus
    singular_noun_counter = Counter()
    sentences = brown.tagged_sents()  # Selecting only 50 sentences
    nouns_list= []
    for sentence in sentences:
        for word, tag in sentence:
            if tag == "NN":
                singular_noun_counter[word] += 1
                nouns_list.append(word.lower())
    
    def remove_word_from_nouns(nouns, word_to_remove):
        """
        Remove all instances of a given word from the nouns list.

        :param nouns: List of nouns
        :param word_to_remove: Word to remove from the list
        :return: Updated list of nouns
        """
        return [noun for noun in nouns if noun != word_to_remove]

    def most_unique_occurrences2(nouns_list, window_size=10, num_words=10):
        unique_counts = {}

        for i, word in enumerate(nouns_list):
            surroundings = tuple(nouns_list[max(0, i - window_size): i] + nouns_list[i + 1: min(len(nouns_list), i + window_size + 1)])
            if word not in unique_counts:
                unique_counts[word] = set()
            unique_counts[word].add(surroundings)
            
        
        words_with_unique_counts = [(word, len(unique_counts[word])) for word in unique_counts]
        sorted_words = sorted(words_with_unique_counts, key=lambda x: x[1], reverse=True)
        return sorted_words
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
    def uniqueness_with_max_neighbor(nouns_list, window_size=10):
        # Get the list of words with their uniqueness values and neighbors
        sorted_words = most_unique_occurrences(nouns_list, window_size)

        # Create a dictionary for quick lookup of uniqueness values
        uniqueness_dict = {word: uniqueness for word, uniqueness, _ in sorted_words}

        # Prepare the final list with maximum neighbor uniqueness values
        result = []
        for word, uniqueness, neighbors in sorted_words:
            max_neighbor_uniqueness = max((uniqueness_dict.get(neighbor, 0) for neighbor in neighbors), default=0)
            result.append((word, uniqueness, max_neighbor_uniqueness))

        return result
    def generate_word_neighbors(word_list, window_size=10, existing_neighbors=None):
        if existing_neighbors is None:
            existing_neighbors = {}

        for i, word in enumerate(word_list):
            neighbors = existing_neighbors.get(word, set())  # Use set instead of list to avoid duplicates
            for j in range(-window_size, window_size + 1):  # Include both ends of the window
                if i + j >= 0 and i + j < len(word_list) and j != 0:  # Exclude the current word itself
                    neighbors.add(word_list[i + j])  # Add neighbors to the set
            existing_neighbors[word] = neighbors
        return existing_neighbors

    # Print uniqueness values and neighbors for each word
    

    def create_a_list_of_values(unique_words_list, num=3):
        values = {}
        for word, uniqueness_value, neighbors in unique_words_list:
            values[word] = uniqueness_value
            max_neighbor_uniqueness = max([neighbor_uniqueness for neighbor_uniqueness in [values.get(neighbor, 0) for neighbor in neighbors]])
            for i in range(num-1):
                values[f"{word}_{i+1}"] = max_neighbor_uniqueness
        return values
    def uniqueness_with_avg_neighbor(nouns_list, window_size=10):
        sorted_words = most_unique_occurrences(nouns_list, window_size)
        uniqueness_dict = {word: uniqueness for word, uniqueness, _ in sorted_words}
        neighbor_dict = {word: neighbors for word, _, neighbors in sorted_words}

        result = []
        for word, uniqueness, neighbors in sorted_words:
            avg_neighbor_uniqueness = sum((uniqueness_dict.get(neighbor, 0) for neighbor in neighbors)) / len(neighbors) if neighbors else 0
            max_neighbor = max(neighbors, key=lambda neighbor: uniqueness_dict.get(neighbor, 0), default=None)
            max_neighbor_of_max_neighbor_uniqueness = 0
            if max_neighbor:
                max_neighbor_neighbors = neighbor_dict.get(max_neighbor, [])
                max_neighbor_of_max_neighbor_uniqueness = max((uniqueness_dict.get(neighbor, 0) for neighbor in max_neighbor_neighbors), default=0)
            
            result.append((word, uniqueness, avg_neighbor_uniqueness, max_neighbor_of_max_neighbor_uniqueness))

        return result

    def check_middle_point(values):
        if len(values) != 3:
            raise ValueError("The input list must contain exactly three values.")
        
        y0, y1, y2 = values

        y_line = y0 + (y2 - y0) / 2

        if y1 > y_line:
            return "above"
        elif y1 < y_line:
            return "below"
        else:
            return "on the line"

    def filter_words(nouns_list, window_size=10):
        extended_uniqueness_list = uniqueness_with_avg_neighbor(nouns_list, window_size)
        filtered_result = []
        for word, uniqueness, avg_neighbor_uniqueness, max_neighbor_of_max_neighbor_uniqueness in extended_uniqueness_list:
            middle_point_check = check_middle_point([uniqueness, avg_neighbor_uniqueness, max_neighbor_of_max_neighbor_uniqueness])
            if middle_point_check == "below" and avg_neighbor_uniqueness <= uniqueness:
                filtered_result.append((word, uniqueness, avg_neighbor_uniqueness, max_neighbor_of_max_neighbor_uniqueness))
        # Sort the filtered result by the uniqueness value of the word
        filtered_result_sorted = sorted(filtered_result, key=lambda x: x[1], reverse=True)
        return filtered_result_sorted

    # Generate the filtered and sorted result list
    filtered_unique_words = filter_words(nouns_list, window_size)

    # Print the filtered and sorted result
    for word, uniqueness_value, avg_neighbor_uniqueness, max_neighbor_of_max_neighbor_uniqueness in filtered_unique_words:
        print(f"Word: {word}, Uniqueness Value: {uniqueness_value}")