import math


class Wordle:
    def __init__(self):
        self._words = self._get_words()
        self._probability_table = self._get_probability_table()
        self._best_word = None
        self._best_entropy = -1
        self._response = None
        self._tries = 0

    def get_best_word(self, interactive: bool = True, wordle_word: str = None) -> tuple:
        if self._response == "ggggg":
            return self._best_word, self._tries
        self._tries += 1
        if self._response:
            self._update_words()
            self._probability_table = self._get_probability_table()
        for word in self._words:
            entropy = self._get_information_entropy(word)
            if entropy > self._best_entropy:
                self._best_entropy = entropy
                self._best_word = word
        if interactive:
            print(
                f"Best word: {self._best_word} of entropy: {self._best_entropy}. Remaining words: {len(self._words)-1}"
            )
        self._best_entropy = -1
        if interactive:
            self._response = input("Enter a response: ")
            return self.get_best_word()
        else:
            self._response = self._get_response(wordle_word=wordle_word, guess_word=self._best_word)
            return self.get_best_word(interactive=False, wordle_word=wordle_word)

    def test_strategy(self) -> float:
        total_number_of_tries = 0
        for word in self._words:
            wordle = Wordle()
            result = wordle.get_best_word(interactive=False, wordle_word=word)
            total_number_of_tries += result[1]
        average_number_of_tries = total_number_of_tries / len(self._words)
        return round(average_number_of_tries, 3)

    @staticmethod
    def _get_words() -> list:
        with open('data/valid_wordles.txt', 'r') as f:
            words = f.read().splitlines()
        return words

    def _get_probability_table(self) -> dict:
        probability_table = {i: {} for i in range(1, 6)}
        for word in self._words:
            for position, letter in enumerate(word, start=1):
                if letter in probability_table[position]:
                    probability_table[position][letter] += 1
                else:
                    probability_table[position][letter] = 1
        for position in probability_table:
            total = sum(probability_table[position].values())
            for letter in probability_table[position]:
                probability_table[position][letter] /= total
        return probability_table

    def _update_words(self):
        for position, (status, letter) in enumerate(zip(self._response, self._best_word)):
            if status == "g":
                self._words = [word for word in self._words if word[position] == letter]
            elif status == "y":
                self._words = [word for word in self._words if letter in word and word[position] != letter]
            elif status == "b":
                self._words = [word for word in self._words if letter not in word]

    def _get_information_entropy(self, word: str) -> float:
        information_entropy = 0
        for position, letter in enumerate(word, start=1):
            probability = self._probability_table[position].get(letter, 0)
            information_entropy += -probability * (math.log2(probability))
        return information_entropy

    @staticmethod
    def _get_response(wordle_word: str, guess_word: str) -> str:
        response = ""
        for wordle_letter, guess_letter in zip(wordle_word, guess_word):
            if wordle_letter == guess_letter:
                response += "g"
            elif guess_letter in wordle_word:
                response += "y"
            else:
                response += "b"
        return response
