from flask import session
import attack
import random

from config import NUMBER_OF_ATTACKS, BASE_FILE_LOCATION, NUMBER_OF_ROUNDS, GRACE_ROUNDS, NUMBER_OF_WORDS
from round import Round

def load_wordlist(path):
    wordlist = []

    with open(path, "r") as file:

        for line in file:
            line = line.strip()
            wordlist.append(line)

    if len(wordlist) == 0:
        raise Exception("No word list loaded!")

    return wordlist

def gen_word_set(wordlist, exp, similarity_type):
    """
    Method creates the entire experiment schema.
    It generates all the words required and places attacks in the #
    """

    words = [None] * NUMBER_OF_ROUNDS

    #Place attention check in position 3 (index 2)
    attention_check_words1 = gen_attention_check(wordlist)
    words[2] = Round(attention_check_words1[0], attention_check_words1[1])

    #Place attention check in position 13 (index 12) - half way through
    attention_check_words3 = gen_attention_check(wordlist)
    words[12] = Round(attention_check_words3[0], attention_check_words3[1])


    #add additional attention check towards end
    s = random.SystemRandom()
    attention_check2 = s.randint(NUMBER_OF_ROUNDS - 3, NUMBER_OF_ROUNDS - 1)
    attention_check_words2 = gen_attention_check(wordlist)
    words[attention_check2] = Round(attention_check_words2[0], attention_check_words2[1])


    # Generates attack positions
    attack_positions = []
    while len(attack_positions) != NUMBER_OF_ATTACKS:
        r = random.SystemRandom()
        position = r.randint(GRACE_ROUNDS, attention_check2 - 1)

        if (not position in attack_positions) and words[position] == None:
            attack_positions.append(position)

    # Sets attack positions
    #SIM_TYPE is {phon, orth} passed in as a GET parameter
    all_attacks = attack.getAttackPairs(similarity_type)
    for a in attack_positions:
        attack_pair = all_attacks.pop()
        words[a] = Round(attack_pair[0], attack_pair[1])

    # Fill the rest with random words
    for i, w in enumerate(words):
        if not w:
            words[i] = Round(get_random_words(wordlist))

    for w in words:
        exp.add_round(w)

    return words


def get_random_words(wordlist):

    words = []
    while len(words) != NUMBER_OF_WORDS:
        position = random.randint(0, len(wordlist) - 1)

        word = wordlist[position]

        if not word in words:
            words.append(word)

    return words

def gen_attention_check(wordlist):

    validResult = False

    while not validResult:

        pair1 = get_random_words(wordlist)
        pair2 = get_random_words(wordlist)

        for p in pair1:

            if p in pair2:
                break

        # If we get to the end without breaking
        # we have a valid pair
        else:
            validResult = True

    return pair1, pair2
