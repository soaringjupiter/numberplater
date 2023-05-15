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


DATELESS_NUMBER_PLATE_PATTERNS = {
    r"^[a-hj-pr-y]{1}[odilrzebasgtyc]{1}$": [1],
    r"^[a-hj-pr-y]{1}[odilrzebasgtyc]{2}$": [1, 2],
    r"^[a-hj-pr-y]{1}[odilrzebasgtyc]{3}$": [1, 2, 3],
    r"^[a-hj-pr-y]{1}[odilrzebasgtyc]{4}$": [1, 2, 3, 4],
    r"^[a-hj-pr-y]{2}[odilrzebasgtyc]{1}$": [2],
    r"^[a-hj-pr-y]{2}[odilrzebasgtyc]{2}$": [2, 3],
    r"^[a-hj-pr-y]{2}[odilrzebasgtyc]{3}$": [2, 3, 4],
    r"^[a-hj-pr-y]{2}[odilrzebasgtyc]{4}$": [2, 3, 4, 5],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{1}$": [3],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{2}$": [3, 4],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{3}$": [3, 4, 5],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{4}$": [3, 4, 5, 6],
    r"^[odilrzebasgtyc]{1}[a-hj-pr-y]{1,3}$": [0],
    r"^[odilrzebasgtyc]{2}[a-hj-pr-y]{1,3}$": [0, 1],
    r"^[odilrzebasgtyc]{3}[a-hj-pr-y]{1,3}$": [0, 1, 2],
    r"^[odilrzebasgtyc]{4}[a-hj-pr-y]{1,3}$": [0, 1, 2, 3],
}

NORTHERN_IRISH_NUMBER_PLATE_PATTERNS = {
    r"^[a-pr-z]{1}(?<=[iz].|.[iz])[odilrzebasgtyc]{1}$": [1],
    r"^[a-pr-z]{1}(?<=[iz].|.[iz])[odilrzebasgtyc]{2}$": [1, 2],
    r"^[a-pr-z]{1}(?<=[iz].|.[iz])[odilrzebasgtyc]{3}$": [1, 2, 3],
    r"^[a-pr-z]{1}(?<=[iz].|.[iz])[odilrzebasgtyc]{4}$": [1, 2, 3, 4],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{1}$": [2],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{2}$": [2, 3],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{3}$": [2, 3, 4],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{4}$": [2, 3, 4, 5],
    r"^[a-pr-z]{3}(?<=[iz].|.[iz])[odilrzebasgtyc]{1}$": [3],
    r"^[a-pr-z]{3}(?<=[iz].|.[iz])[odilrzebasgtyc]{2}$": [3, 4],
    r"^[a-pr-z]{3}(?<=[iz].|.[iz])[odilrzebasgtyc]{3}$": [3, 4, 5],
    r"^[a-pr-z]{3}(?<=[iz].|.[iz])[odilrzebasgtyc]{4}$": [3, 4, 5, 6],
    r"^[odilrzebasgtyc]{1}(?=.*[iz])[a-pr-z]{1,3}$": [0],
    r"^[odilrzebasgtyc]{2}(?=.*[iz])[a-pr-z]{1,3}$": [0, 1],
    r"^[odilrzebasgtyc]{3}(?=.*[iz])[a-pr-z]{1,3}$": [0, 1, 2],
    r"^[odilrzebasgtyc]{4}(?=.*[iz])[a-pr-z]{1,3}$": [0, 1, 2, 3],
}

SUFFIX_NUMBER_PLATE_PATTERNS = {
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{1}[a-npr-tv-z]{1}$": [3],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{2}[a-npr-tv-z]{1}$": [3, 4],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{3}[a-npr-tv-z]{1}$": [3, 4, 5],
}

PREFIX_NUMBER_PLATE_PATTERNS = {
    r"^[a-npr-tv-z]{1}[odilrzebasgtyc]{1}[a-hj-pr-y]{3}$": [1],
    r"^[a-npr-tv-z]{1}[odilrzebasgtyc]{2}[a-hj-pr-y]{3}$": [1, 2],
    r"^[a-npr-tv-z]{1}[odilrzebasgtyc]{3}[a-hj-pr-y]{3}$": [1, 2, 3],
}

CURRENT_NUMBER_PLATE_PATTERNS = {
    r"^[a-hj-pr-y]{2}[odilrzebasgtyc]{2}[a-z]{1}$": [2, 3],
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
        patterns = {}
        if args.dateless or args.all:
            patterns.update(DATELESS_NUMBER_PLATE_PATTERNS)
        if args.northern_irish or args.all:
            patterns.update(NORTHERN_IRISH_NUMBER_PLATE_PATTERNS)
        if args.suffix or args.all:
            patterns.update(SUFFIX_NUMBER_PLATE_PATTERNS)
        if args.prefix or args.all:
            patterns.update(PREFIX_NUMBER_PLATE_PATTERNS)
        if args.current or args.all:
            patterns.update(CURRENT_NUMBER_PLATE_PATTERNS)

        for pattern, indices in patterns.items():
            if re.match(pattern, word):
                copy_of_word = word
                list_of_letters = [letters[copy_of_word[index]] for index in indices]
                if len(list_of_letters) > 1:
                    for combination in itertools.product(*list_of_letters):
                        score = 0
                        i = 0
                        temp_word = copy_of_word
                        for index in indices:
                            temp_word = (
                                temp_word[:index]
                                + combination[i][0]
                                + temp_word[index + 1 :]
                            )
                            score += combination[i][1]
                            i += 1
                        score += sum(2 for char in temp_word if char.isalpha())
                        words[word].add((temp_word, score))
                else:
                    for letter in list_of_letters[0]:
                        temp_word = (
                            copy_of_word[: indices[0]]
                            + letter[0]
                            + copy_of_word[indices[0] + 1 :]
                        )
                        score = letter[1] + sum(
                            2 for char in temp_word if char.isalpha()
                        )
                        words[word].add((temp_word, score))

    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

    # Save the words-dict to a file:
    if not args.input_word:
        with open("words.json", "w") as f:
            json.dump(words, f, default=set_default, indent=2)
    else:
        tuples = set.union(*words.values())
        sorted_number_plates_by_score = [
            tuple[0] for tuple in sorted(tuples, key=lambda x: x[1], reverse=True)
        ]
        print(sorted_number_plates_by_score)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input_word",
        help="The word you want to check if it can be written with numbers that look like letters",
        type=str,
        nargs="?",
    )

    parser.add_argument(
        "-d",
        "--dateless",
        action="store_true",
        help="Use this flag if you want to check if the word can be written on a dateless number plate",
    )

    parser.add_argument(
        "-n",
        "--northern-irish",
        action="store_true",
        help="Use this flag if you want to check if the word can be written on a Northern Irish number plate",
    )

    parser.add_argument(
        "-s",
        "--suffix",
        action="store_true",
        help="Use this flag if you want to check if the word can be written on a suffix number plate",
    )

    parser.add_argument(
        "-p",
        "--prefix",
        action="store_true",
        help="Use this flag if you want to check if the word can be written on a prefix number plate",
    )

    parser.add_argument(
        "-c",
        "--current",
        action="store_true",
        help="Use this flag if you want to check if the word can be written on a current number plate",
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Use this flag if you want to check if the word can be written on any type of number plate",
    )

    args = parser.parse_args()

    main()
