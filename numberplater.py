import json
import re
import os
import itertools
import argparse


# Function that takes a list, doubles its length and the new elements are empty:
def double_list_length(list):
    length = len(list)
    for i in range(length):
        list.append("")
    return list


# Match 0, 1 or 2 letters at the beginning of a string, followed by 1 or 2 of the following letters: o, d, i, l, r, z, e, b, a, s, g, t, y, c, followed lastly by 0, 1, 2 or 3 letters and then the end of the string:

PATTERN = r"^[a-z]{0,2}[odilrzebasgtyc]{1,2}[a-z]{0,3}$"

# Match 1-3 letters at the beginning of a string, followed bt 1-4 of the following letters: o, d, i, l, r, z, e, b, a, s, g, t, y, c:

PATTERN_DATELESS = r"^[a-z]{1,3}[odilrzebasgtyc]{1,4}$"

PATTERN_FOR_1_LETTER_WORDS = {r"^[odilrzebasgtyc]{1}$": [0]}

PATTERN_FOR_2_LETTER_WORDS = {
    r"^[a-z]{1}[odilrzebasgtyc]{1}$": [1],
    r"^[odilrzebasgtyc]{1}[a-z]{1}$": [0],
    r"^[odilrzebasgtyc]{2}$": [0, 1],
}

PATTERN_FOR_3_LETTER_WORDS = {
    r"^[a-z]{1}[odilrzebasgtyc]{1}[a-z]{1}$": [1],
    r"^[a-z]{1}[odilrzebasgtyc]{2}$": [1, 2],
    r"^[a-z]{2}[odilrzebasgtyc]{1}$": [2],
    r"^[odilrzebasgtyc]{1}[a-z]{2}$": [0],
    r"^[odilrzebasgtyc]{2}[a-z]{1}$": [0, 1],
}

PATTERN_FOR_4_LETTER_WORDS = {
    r"^[a-z]{1}[odilrzebasgtyc]{1}[a-z]{2}$": [1],
    r"^[a-z]{1}[odilrzebasgtyc]{2}[a-z]{1}$": [1, 2],
    r"^[a-z]{1}[odilrzebasgtyc]{3}": [1, 2, 3],
    r"^[a-z]{2}[odilrzebasgtyc]{1}[a-z]{1}$": [2],
    r"^[a-z]{2}[odilrzebasgtyc]{2}$": [2, 3],
    r"^[a-z]{3}[odilrzebasgtyc]{1}$": [3],
    r"^[odilrzebasgtyc]{1}[a-z]{3}$": [0],
    r"^[odilrzebasgtyc]{2}[a-z]{2}$": [0, 1],
    r"^[odilrzebasgtyc]{3}[a-z]{1}$": [0, 1, 2],
}

PATTERN_FOR_5_LETTER_WORDS = {
    r"^[a-z]{1}[odilrzebasgtyc]{1}[a-z]{3}$": [1],
    r"^[a-z]{1}[odilrzebasgtyc]{2}[a-z]{2}$": [1, 2],
    r"^[a-z]{1}[odilrzebasgtyc]{3}[a-z]{1}$": [1, 2, 3],
    r"^[a-z]{1}[odilrzebasgtyc]{4}$": [1, 2, 3, 4],
    r"^[a-z]{2}[odilrzebasgtyc]{1}[a-z]{2}$": [2],
    r"^[a-z]{2}[odilrzebasgtyc]{2}[a-z]{1}$": [2, 3],
    r"^[a-z]{2}[odilrzebasgtyc]{3}$": [2, 3, 4],
    r"^[a-z]{3}[odilrzebasgtyc]{1}[a-z]{1}$": [3],
    r"^[a-z]{3}[odilrzebasgtyc]{2}$": [3, 4],
    r"^[odilrzebasgtyc]{2}[a-z]{3}$": [0, 1],
    r"^[odilrzebasgtyc]{3}[a-z]{2}$": [0, 1, 2],
    r"^[odilrzebasgtyc]{4}[a-z]{1}$": [0, 1, 2, 3],
}

PATTERN_FOR_6_LETTER_WORDS = {
    r"^[a-z]{1}[odilrzebasgtyc]{2}[a-z]{3}$": [1, 2],
    r"^[a-z]{2}[odilrzebasgtyc]{1}[a-z]{3}$": [2],
    r"^[a-z]{2}[odilrzebasgtyc]{4}$": [2, 3, 4, 5],
    r"^[a-z]{2}[odilrzebasgtyc]{2}[a-z]{2}$": [2, 3],
    r"^[a-z]{2}[odilrzebasgtyc]{3}[a-z]{1}$": [2, 3, 4],
    r"^[a-z]{3}[odilrzebasgtyc]{3}$": [3, 4, 5],
    r"^[a-z]{3}[odilrzebasgtyc]{2}[a-z]{1}$": [3, 4],
    r"^[odilrzebasgtyc]{3}[a-z]{3}$": [0, 1, 2],
    r"^[odilrzebasgtyc]{4}[a-z]{2}$": [0, 1, 2, 3],
}

PATTERN_FOR_7_LETTER_WORDS = {
    r"^[a-z]{1}[odilrzebasgtyc]{3}[a-z]{3}$": [1, 2, 3],
    r"^[a-z]{2}[odilrzebasgtyc]{2}[a-z]{3}$": [2, 3],
    r"^[a-z]{3}[odilrzebasgtyc]{1}[a-z]{3}$": [3],
    r"^[a-z]{3}[odilrzebasgtyc]{2}[a-z]{2}$": [3, 4],
    r"^[a-z]{3}[odilrzebasgtyc]{3}[a-z]{1}$": [3, 4, 5],
    r"^[a-z]{3}[odilrzebasgtyc]{4}$": [3, 4, 5, 6],
    r"^[odilrzebasgtyc]{4}[a-z]{3}$": [0, 1, 2, 3],
}


def main():
    # Dict that has letters as keys and a list of numbers that look like that letter as values:
    letters = {
        "o": [("0", 1), ("6", 0.5), ("8", 0.5), ("9", 0.5)],
        "d": [("0", 0.5)],
        "i": [("1", 1)],
        "l": [("1", 1)],
        "r": [("2", 0.5)],
        "z": [("2", 1)],
        "e": [("3", 1)],
        "b": [("3", 0.5), ("6", 1), ("8", 0.5)],
        "a": [("4", 1), ("8", 0.5)],
        "s": [("5", 0.5)],
        "g": [("6", 0.5), ("9", 0.5)],
        "t": [("7", 1)],
        "y": [("7", 0.5)],
        "c": [("6", 0.5)],
    }

    # Set working directory to the folder where the file is located:
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Import words.txt (which is a plaintext file with one word per line) and save all the words that match either of the patterns to a python dictionary with an empty set as value:
    if not args.input_word:
        with open("words.txt", encoding="UTF-8") as f:
            words = f.read().splitlines()
            words = [
                word
                for word in words
                if re.match(PATTERN, word) or re.match(PATTERN_DATELESS, word)
            ]
            words = {word: set() for word in words}
    else:
        words = {args.input_word: set()}

    # For each key in words, go through the appropriate dict of patterns and for each pattern that matches the key, use the value of the pattern as a list of indices to replace the letters with the numbers that look like them, and if a letter has multiple numbers that look like it, create all possible strings using each number once and add them to the list of values for the key:

    for word in words:
        if len(word) == 1:
            appropriate_pattern = PATTERN_FOR_1_LETTER_WORDS
        elif len(word) == 2:
            appropriate_pattern = PATTERN_FOR_2_LETTER_WORDS
        elif len(word) == 3:
            appropriate_pattern = PATTERN_FOR_3_LETTER_WORDS
        elif len(word) == 4:
            appropriate_pattern = PATTERN_FOR_4_LETTER_WORDS
        elif len(word) == 5:
            appropriate_pattern = PATTERN_FOR_5_LETTER_WORDS
        elif len(word) == 6:
            appropriate_pattern = PATTERN_FOR_6_LETTER_WORDS
        elif len(word) == 7:
            appropriate_pattern = PATTERN_FOR_7_LETTER_WORDS

        for pattern, indices in appropriate_pattern.items():
            if re.match(pattern, word):
                copy_of_word = word
                list_of_letters = [letters[copy_of_word[index]] for index in indices]
                if len(list_of_letters) > 1:
                    for combination in itertools.product(*list_of_letters):
                        i = 0
                        temp_word = copy_of_word
                        for index in indices:
                            temp_word = (
                                temp_word[:index]
                                + combination[i][0]
                                + temp_word[index + 1 :]
                            )
                            i += 1
                        words[word].add(temp_word)
                else:
                    for letter in list_of_letters[0]:
                        words[word].add(
                            copy_of_word[: indices[0]]
                            + letter[0]
                            + copy_of_word[indices[0] + 1 :]
                        )

    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

    # Save the words-dict to a file:
    if not args.input_word:
        with open("words.json", "w") as f:
            json.dump(words, f, default=set_default, indent=2)
    else:
        print(words[args.input_word])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input_word",
        help="The word you want to check if it can be written with numbers that look like letters",
        type=str,
        nargs="?",
    )

    args = parser.parse_args()

    main()
