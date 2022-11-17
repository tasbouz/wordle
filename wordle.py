import math
import re
from collections import Counter

from tqdm import tqdm


class Wordle:
    """A Wordle Solver.

    Parameters
    ----------
    path_to_available_words : str
        The path to the .txt file containiing all available words.
    """

    def __init__(self, path_to_available_words: str, solution=None):
        self.path_to_available_words = path_to_available_words
        self.attempts = 1
        self.solution = solution  # when solution is known we can evaluate the model

        with open(self.path_to_available_words, "r") as file:
            self.all_words = file.read().splitlines()

        if len(set([len(word) for word in self.all_words])) == 1:
            self.words_length = len(self.all_words[0])
            self.available_words = self.all_words
        else:
            raise ValueError('All words must have the same length.')

    def wordle(self) -> tuple:
        """Main method for solving wordle.

        Returns
        -------
        tuple
            A tuple containing the correct word and the numbers of attempts.
        """
        guess_word = self._word_guesser(self.available_words)

        if not self.solution:
            response = input(f"Try: '{guess_word}'. \n Response (b/y/g): ")
        else:
            response = self._response_generator(guess_word)

        if response == "ggggg":  # response = "ggggg" -> correct guess word
            return guess_word, self.attempts
        else:
            self._available_words_updater(guess_word=guess_word, response=response)
            self.attempts += 1
            return Wordle.wordle(self)

    def evaluator(self) -> float:
        """Evaluator of wordle algorithm.

        Returns
        -------
        float
            Average number of attempts to reach solution.
        """
        summ, n = 0, 0
        for word in tqdm(self.all_words):
            summ += Wordle(path_to_available_words=self.path_to_available_words, solution=word).wordle()[1]
            n += 1

        return summ / n

    def _available_words_updater(self, guess_word, response):
        counter = 0
        for letter_in_response, letter_in_guess_word in zip(response, guess_word):
            if letter_in_response == "b":
                # if letter exists only once, then remove all words including the letter
                if len([m.start() for m in re.finditer(letter_in_guess_word, guess_word)]) == 1:
                    self.available_words = [word for word in self.available_words if word.find(letter_in_guess_word) == -1]
                # if letter exists more than once, remove all words that include this letter in the current position
                else:
                    self.available_words = [
                        word
                        for word in self.available_words
                        if counter not in [m.start() for m in re.finditer(letter_in_guess_word, word)]
                    ]
            elif letter_in_response == "y":
                # if letter exists once, remove all words not including the letter or include it in the current position
                if len([m.start() for m in re.finditer(letter_in_guess_word, guess_word)]) == 1:
                    self.available_words = [word for word in self.available_words if word.find(letter_in_guess_word) not in [-1, counter]]
                # if letter exists more than once then remove all words that include this letter in the current position
                else:
                    self.available_words = [
                        word
                        for word in self.available_words
                        if counter not in [m.start() for m in re.finditer(letter_in_guess_word, word)]
                    ]
            elif letter_in_response == "g":
                self.available_words = [
                    word for word in self.available_words if counter in [m.start() for m in re.finditer(letter_in_guess_word, word)]
                ]
            else:
                print("Not a valid repsponse. Bye!")
                return
            counter += 1

    def _response_generator(self, guess_word):
        response = str()
        for letter_in_guess_word, letter_in_solution in zip(guess_word, self.solution):
            if letter_in_guess_word == letter_in_solution:
                response += "g"
            elif (letter_in_guess_word != letter_in_solution) and (letter_in_guess_word in self.solution):
                response += "y"
            else:
                response += "b"
        return response

    def _word_guesser(self, word_list):

        def _entropy(word, probability_matrix):
            word_entropy = 0
            for k, v in enumerate(word):
                letter_probability = probability_matrix[k][v]
                word_entropy -= letter_probability * math.log(letter_probability, 2)

            return word_entropy

        # compute occurences of letters in each position for each word
        occurences = {k: [word[k] for word in word_list] for k in range(self.words_length)}

        # compute distributions of letters in each position using occurences
        distributions = {k: dict(Counter(v)) for k, v in occurences.items()}

        # compute probabilities of letters in each position using distributions
        probabilities = {k: {j: distributions[k][j] / len(word_list) for j in distributions[k]} for k in
                         range(self.words_length)}

        # compute entropies of letters in each position using entropy function
        entropies = {word: _entropy(word, probabilities) for word in word_list}

        # return the word with maximum entropy
        return max(entropies, key=entropies.get)


if __name__ == "__main__":
    avg_attempts = Wordle(path_to_available_words="words.txt").evaluator()
    print(avg_attempts)
