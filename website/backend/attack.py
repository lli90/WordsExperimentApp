import random
import json

from config import BASE_FILE_LOCATION
from config import NUMBER_OF_ATTACKS

def getAttackPairs():
    with open(f"{BASE_FILE_LOCATION}data/attackPairs.json", "r") as f:
        data = f.read()

    attack_pairs = json.loads(data)
        
    all_attacks = []
    for attack_no in range(NUMBER_OF_ATTACKS):
        r = random.SystemRandom()
        next_attack_index = r.randint(0, len(attack_pairs['pairs']) - 1)
        
        all_attacks.append(attack_pairs['pairs'].pop(next_attack_index))
    
    for attack in all_attacks:
        for i in range(2):
                attack[i] = attack[i].split(',')
    return all_attacks
   
