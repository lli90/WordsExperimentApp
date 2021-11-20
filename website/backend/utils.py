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

def gen_word_set(wordlist, exp):
    """
    Method creates the entire experiment schema. 
    It generates all the words required and places attacks in the #
    """

    words = [None] * NUMBER_OF_ROUNDS

    # Generates attack positions
    attackPositions = []
    while True:

        r = random.SystemRandom()

        position = r.randint(GRACE_ROUNDS + 1, NUMBER_OF_ROUNDS) - 1

        if not position in attackPositions:
            attackPositions.append(position)
        
        if len(attackPositions) == NUMBER_OF_ATTACKS: break

    # Sets attack positions
    for a in attackPositions:
        attackPair = attack.getAttackPair()
        words[a] = Round(attackPair[0], attackPair[1])

    # Place attension check in position 3 (index 2)
    attensionCheckWords1 = gen_attension_check(wordlist)
    words[2] = Round(attensionCheckWords1[0], attensionCheckWords1[1])

    #add additional attention check towards end
    s = random.SystemRandom()
    attention_check2 = s.randint(NUMBER_OF_ROUNDS - 3, NUMBER_OF_ROUNDS)
    attensionCheckWords2 = gen_attension_check(wordlist)
    words[attention_check2] = Round(attensionCheckWords2[0], attensionCheckWords2[1])

    # Fill the rest with random words
    for i, w in enumerate(words):
        if not w:
            words[i] = Round(get_random_words(wordlist))

    for w in words:
        exp.add_round(w)

    return words

def get_random_words(wordlist):

    words = []
    while True:
        position = random.randint(0, len(wordlist) - 1)
        
        word = wordlist[position]

        if not word in words:
            words.append(word)

        if len(words) == NUMBER_OF_WORDS: break
    return words

def gen_attension_check(wordlist):

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
