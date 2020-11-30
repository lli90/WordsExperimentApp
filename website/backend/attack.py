import random
import json

from config import BASE_FILE_LOCATION

def getAttackPair():
    with open(f"{BASE_FILE_LOCATION}data/attackPairs.json") as f:
        data = f.read()

    attackPairs = json.loads(data)

    pairs = random.choice(attackPairs["pairs"])

    pairs[0] = pairs[0].split(",")
    pairs[1] = pairs[1].split(",")

    return pairs