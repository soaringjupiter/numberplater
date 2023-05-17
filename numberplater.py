import datetime
import json
import re
import os
import itertools
import argparse
import string
import sys


def check_input_word(word):
    if len(word) > 7:
        raise ValueError("The input word must be 7 characters or less.")
    return word


def handle_wildcards(word):
    # If there are no wildcards, return the word in a set.
    if "*" not in word:
        return {word: set()}
    else:
        # If there are more than one wildcard, raise an error.
        if word.count("*") > 1:
            raise ValueError(
                "Currently only one wildcard is supported. Support for multiple wildcards will be added in a future update."
            )
        # If there is a wildcard, create a dictionary of all possible words.
        words = {}
        # For each letter in the alphabet, replace the wildcard with the letter.
        for letter in string.ascii_lowercase:
            new_word = word.replace("*", letter)
            words[new_word] = set()
        # Also add the word with the wildcard removed.
        words[word.replace("*", "")] = set()
        return words


def get_issuable_years():
    # Get the current year:
    current_year = datetime.datetime.now().year % 100
    # Get the current month:
    current_month = datetime.datetime.now().month
    issued_years = []
    for x in range(1, current_year + 1):
        if x != 1:
            issued_years.append(str(x).zfill(2))
        if x != current_year or current_month >= 7.0:
            issued_years.append(str(x + 50).zfill(2))
    return issued_years


# Regex patterns for number plates:
# Dateless number plates consist of 1-3 letters followed by 1-4 numbers or 1-4 numbers followed by 1-3 letters.
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


# Northern Irish number plates consist of 1-3 letters (containing i or z) followed by 1-4 numbers
# or 1-4 numbers followed by 1-3 letters (containing i or z).
NORTHERN_IRISH_NUMBER_PLATE_PATTERNS = {
    r"^[a-pr-z]{1}(?<=[iz])[odilrzebasgtyc]{1}$": [1],
    r"^[a-pr-z]{1}(?<=[iz])[odilrzebasgtyc]{2}$": [1, 2],
    r"^[a-pr-z]{1}(?<=[iz])[odilrzebasgtyc]{3}$": [1, 2, 3],
    r"^[a-pr-z]{1}(?<=[iz])[odilrzebasgtyc]{4}$": [1, 2, 3, 4],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{1}$": [2],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{2}$": [2, 3],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{3}$": [2, 3, 4],
    r"^[a-pr-z]{2}(?<=[iz].|.[iz])[odilrzebasgtyc]{4}$": [2, 3, 4, 5],
    r"^[a-pr-z]{3}(?<=[iz]..|.[iz].|..[iz])[odilrzebasgtyc]{1}$": [3],
    r"^[a-pr-z]{3}(?<=[iz]..|.[iz].|..[iz])[odilrzebasgtyc]{2}$": [3, 4],
    r"^[a-pr-z]{3}(?<=[iz]..|.[iz].|..[iz])[odilrzebasgtyc]{3}$": [3, 4, 5],
    r"^[a-pr-z]{3}(?<=[iz]..|.[iz].|..[iz])[odilrzebasgtyc]{4}$": [3, 4, 5, 6],
    r"^[odilrzebasgtyc]{1}(?=.*[iz])[a-pr-z]{1,3}$": [0],
    r"^[odilrzebasgtyc]{2}(?=.*[iz])[a-pr-z]{1,3}$": [0, 1],
    r"^[odilrzebasgtyc]{3}(?=.*[iz])[a-pr-z]{1,3}$": [0, 1, 2],
    r"^[odilrzebasgtyc]{4}(?=.*[iz])[a-pr-z]{1,3}$": [0, 1, 2, 3],
}

# Suffix number plates consist of 3 letters followed by 1-3 numbers and then a single letter.
SUFFIX_NUMBER_PLATE_PATTERNS = {
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{1}[a-npr-tv-z]{1}$": [3],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{2}[a-npr-tv-z]{1}$": [3, 4],
    r"^[a-hj-pr-y]{3}[odilrzebasgtyc]{3}[a-npr-tv-z]{1}$": [3, 4, 5],
}

# Prefix number plates consist of a single letter followed by 1-3 numbers and then 3 letters.
PREFIX_NUMBER_PLATE_PATTERNS = {
    r"^[a-npr-tv-z]{1}[odilrzebasgtyc]{1}[a-hj-pr-y]{3}$": [1],
    r"^[a-npr-tv-z]{1}[odilrzebasgtyc]{2}[a-hj-pr-y]{3}$": [1, 2],
    r"^[a-npr-tv-z]{1}[odilrzebasgtyc]{3}[a-hj-pr-y]{3}$": [1, 2, 3],
}

# Current number plates consist of 2 letters followed by 2 numbers and then 3 letters.
CURRENT_NUMBER_PLATE_PATTERNS = {
    r"^[a-hj-pr-y]{2}[odilrzebasgtyc]{2}[a-z]{3}$": [2, 3],
}


def main():
    # Dict that has letters as keys and a list of numbers that look like that letter as values:
    issuable_years = get_issuable_years()
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
        check_input_word(args.input_word)
        words = handle_wildcards(args.input_word)

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
                list_of_letters = [letters[word[index]] for index in indices]
                if len(list_of_letters) > 1:
                    for combination in itertools.product(*list_of_letters):
                        score = 0
                        i = 0
                        temp_word = word
                        for index in indices:
                            temp_word = (
                                temp_word[:index]
                                + combination[i][0]
                                + temp_word[index + 1 :]
                            )
                            score += combination[i][1]
                            i += 1
                        if (
                            pattern in CURRENT_NUMBER_PLATE_PATTERNS
                            and not args.ignore_year
                        ):
                            if int(temp_word[2:4]) not in issuable_years:
                                continue
                        score += sum(2 for char in temp_word if char.isalpha())
                        words[word].add((temp_word, score))
                else:
                    for letter in list_of_letters[0]:
                        temp_word = (
                            word[: indices[0]] + letter[0] + word[indices[0] + 1 :]
                        )
                        score = letter[1] + sum(
                            2 for char in temp_word if char.isalpha()
                        )
                        words[word].add((temp_word, score))

    def set_default(obj):
        """Converts sets to lists, so they can be serialized."""
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

    parser.add_argument(
        "--ignore_year",
        action="store_true",
        help="Use this flag if you want to include number plates that cannot currently be issued",
    )

    # if no flags are set, set the default to -a:
    if len(sys.argv) == 2:
        parser.set_defaults(all=True)

    args = parser.parse_args()

    main()
