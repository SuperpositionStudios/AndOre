import os
import json
import string


class Smelter:

    def __init__(self):
        self.whitelisted_words = set()
        self.punctiation_set = set(string.punctuation)
        # Generate whitelisted_words set
        with open(self.path_to_this_files_directory() + 'word_whitelist.json') as json_data:
            d = json.load(json_data)

            # List of characters we're excluding (punctuation)
            self.punctiation_set.add('"')
            self.punctiation_set.add("'")
            self.punctiation_set.add('-')

            # Looping through all the stories in the json file
            stories = d.get('stories', [])
            for story in stories:
                sanitized_string = ''.join(
                    ch for ch in story if ch not in self.punctiation_set)  # Removing the punctuation from the story
                sanitized_string = sanitized_string.lower()
                self.whitelisted_words = self.whitelisted_words | set(sanitized_string.split(' '))  # Merging sets

            # Adding the whitelisted words to our set
            self.whitelisted_words = self.whitelisted_words | set(d.get('approved_words', []))

            # Adding the game specific words to our set
            self.whitelisted_words = self.whitelisted_words | set(d.get('game_terms', []))

            # For our information
            self.whitelisted_words.remove('')

    def path_to_this_files_directory(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return dir_path + '/'

    def filter_word(self, word):
        sanitized_word = str(word).lower()
        sanitized_word = ''.join(ch for ch in sanitized_word if ch not in self.punctiation_set)
        try:
            val = int(sanitized_word)
            return val
        except ValueError:
            if sanitized_word in self.whitelisted_words:
                return word
            else:
                return 'heck'

    def filter_sentence(self, sentence):
        words = sentence.split(' ')
        new_words = []
        for word in words:
            new_words.append(self.filter_word(word))
        new_sentence = ""
        for word in new_words:
            new_sentence += word + " "
        return new_sentence

    def number_of_whitelisted_words(self):
        return self.whitelisted_words.__len__()
